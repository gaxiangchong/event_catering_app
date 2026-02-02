from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Event, MealOption, Order, OrderStatus
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import os
import stripe

bp = Blueprint('payment', __name__, url_prefix='/payment')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        event_id = request.args.get('event_id')
        meal_id = request.args.get('meal_id')
        
        if not event_id or not meal_id:
            flash('Invalid Booking Request', 'error')
            return redirect(url_for('events.list_events'))
        
        event = Event.query.get_or_404(event_id)
        meal = MealOption.query.get_or_404(meal_id)
        
        # Check for existing PAID order
        existing_order = Order.query.filter_by(
            user_id=current_user.id, 
            event_id=event.id, 
            status=OrderStatus.PAID
        ).first()
        
        if existing_order:
            flash('You have already booked this event!', 'warning')
            return redirect(url_for('events.list_events'))
        
        # Calculate total amount
        total_amount = event.fee + event.admin_fee

        return render_template('payment/checkout.html', event=event, meal=meal, total_amount=total_amount)

    elif request.method == 'POST':
        event_id = request.form.get('event_id')
        meal_id = request.form.get('meal_id')
        payment_method = request.form.get('payment_method')
        
        event = Event.query.get_or_404(event_id)
        meal = MealOption.query.get_or_404(meal_id)
        
        # Verify meal belongs to event
        if meal.event_id != event.id:
            abort(400)

        # Check existing again
        existing_order = Order.query.filter_by(
            user_id=current_user.id, 
            event_id=event.id, 
            status=OrderStatus.PAID
        ).first()
        
        if existing_order:
            flash('You have already booked this event!', 'warning')
            return redirect(url_for('events.list_events'))
        
        # Calculate total amount
        total_amount = event.fee + event.admin_fee

        if payment_method == 'stripe':
            return redirect(url_for('payment.stripe_payment', 
                                  event_id=event_id, 
                                  meal_id=meal_id))
        elif payment_method == 'touchngo':
            # Handle Touch n Go payment with file upload
            if 'payment_screenshot' not in request.files:
                flash('Please upload a payment screenshot', 'error')
                return redirect(url_for('payment.checkout', event_id=event_id, meal_id=meal_id))
            
            file = request.files['payment_screenshot']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('payment.checkout', event_id=event_id, meal_id=meal_id))
            
            if file and allowed_file(file.filename):
                # Create order first to get ID
                order = Order(
                    user_id=current_user.id,
                    event_id=event.id,
                    meal_option_id=meal.id,
                    amount=event.fee,
                    admin_fee=event.admin_fee,
                    status=OrderStatus.PROCESSING,
                    payment_method='touchngo'
                )
                db.session.add(order)
                db.session.flush()  # Get order ID
                
                # Save file with unique name
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
                
                # Ensure upload directory exists
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                order.payment_screenshot = filename
                db.session.commit()
                
                return redirect(url_for('payment.touchngo_confirmation', order_id=order.id))
            else:
                flash('Invalid file type. Please upload a PNG, JPG, or JPEG image.', 'error')
                return redirect(url_for('payment.checkout', event_id=event_id, meal_id=meal_id))
        else:
            flash('Invalid payment method', 'error')
            return redirect(url_for('payment.checkout', event_id=event_id, meal_id=meal_id))

@bp.route('/stripe/<int:event_id>/<int:meal_id>')
@login_required
def stripe_payment(event_id, meal_id):
    """Create Stripe checkout session"""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    event = Event.query.get_or_404(event_id)
    meal = MealOption.query.get_or_404(meal_id)
    
    # Verify meal belongs to event
    if meal.event_id != event.id:
        abort(400)
    
    # Create pending order
    order = Order(
        user_id=current_user.id,
        event_id=event.id,
        meal_option_id=meal.id,
        amount=event.fee,
        admin_fee=event.admin_fee,
        status=OrderStatus.PENDING,
        payment_method='stripe',
        payment_reference=str(uuid.uuid4())
    )
    db.session.add(order)
    db.session.commit()
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': current_app.config['STRIPE_CURRENCY'],
                        'unit_amount': int(event.fee * 100),  # Convert to cents
                        'product_data': {
                            'name': f'{event.title} - {meal.name}',
                            'description': f'Event on {event.date.strftime("%B %d, %Y")}',
                        },
                    },
                    'quantity': 1,
                },
                {
                    'price_data': {
                        'currency': current_app.config['STRIPE_CURRENCY'],
                        'unit_amount': int(event.admin_fee * 100),  # Convert to cents
                        'product_data': {
                            'name': 'Admin Fee',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('payment.stripe_success', order_id=order.id, _external=True),
            cancel_url=url_for('payment.stripe_cancel', order_id=order.id, _external=True),
        )
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        order.status = OrderStatus.FAILED
        db.session.commit()
        flash(f'Payment error: {str(e)}', 'error')
        return redirect(url_for('events.list_events'))

@bp.route('/stripe/success/<int:order_id>')
@login_required
def stripe_success(order_id):
    """Handle successful Stripe payment"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        abort(403)
    
    # Update order status
    order.status = OrderStatus.PAID
    order.payment_reference = f"STRIPE-{uuid.uuid4().hex[:10].upper()}"
    db.session.commit()
    
    return redirect(url_for('payment.result', order_id=order.id))

@bp.route('/stripe/cancel/<int:order_id>')
@login_required
def stripe_cancel(order_id):
    """Handle cancelled Stripe payment"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        abort(403)
    
    order.status = OrderStatus.FAILED
    db.session.commit()
    
    return redirect(url_for('payment.result', order_id=order.id))

@bp.route('/touchngo/confirmation/<int:order_id>')
@login_required
def touchngo_confirmation(order_id):
    """Show Touch n Go payment confirmation"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        abort(403)
    
    return render_template('payment/touchngo_confirmation.html', order=order)

@bp.route('/result/<int:order_id>')
@login_required
def result(order_id):
    """Show payment result"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        abort(403)
        
    return render_template('payment/result.html', order=order)
