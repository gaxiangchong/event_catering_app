from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Event, EventStatus, MealOption, Order, OrderStatus
import csv
from io import StringIO, BytesIO
from flask import Response, stream_with_context, send_file
from openpyxl import Workbook
from datetime import datetime
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('auth.login')) # Or admin login
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        telephone = request.form.get('telephone')
        # Admin login is same as user login but checks is_admin flag.
        # In a real app, maybe a password? For now, adhering to simple auth but checking flag.
        
        user = User.query.filter_by(telephone=telephone).first()
        if user and user.is_admin:
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@bp.route('/dashboard')
@admin_required
def dashboard():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin/dashboard.html', events=events)

@bp.route('/events/new', methods=['GET', 'POST'])
@admin_required
def new_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date') # Expecting YYYY-MM-DDTHH:MM
        location = request.form.get('location')
        fee = request.form.get('fee')
        admin_fee = request.form.get('admin_fee', '1.0')
        capacity = request.form.get('capacity')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            event = Event(
                title=title,
                description=description,
                date=date_obj,
                location=location,
                fee=float(fee),
                admin_fee=float(admin_fee),
                capacity=int(capacity) if capacity else None,
                status=EventStatus.ACTIVE
            )
            db.session.add(event)
            db.session.flush()  # Get ID

            # Add two standard meal options: Standard and Vegetarian
            meal_0_name = request.form.get('meal_0_name') or 'Standard'
            meal_0_desc = request.form.get('meal_0_description') or ''
            meal_1_name = request.form.get('meal_1_name') or 'Vegetarian'
            meal_1_desc = request.form.get('meal_1_description') or ''
            for name, desc in [(meal_0_name, meal_0_desc), (meal_1_name, meal_1_desc)]:
                meal = MealOption(event_id=event.id, name=name, description=desc or None)
                db.session.add(meal)

            db.session.commit()
            flash('Event created successfully!')
            return redirect(url_for('admin.dashboard'))
        except ValueError:
            flash('Invalid date or fee format.', 'error')
            
    return render_template('admin/event_form.html', event=None)

@bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        date_str = request.form.get('date')
        event.location = request.form.get('location')
        event.fee = float(request.form.get('fee'))
        event.admin_fee = float(request.form.get('admin_fee', '1.0'))
        event.capacity = int(request.form.get('capacity')) if request.form.get('capacity') else None

        meal_0_name = request.form.get('meal_0_name') or 'Standard'
        meal_0_desc = request.form.get('meal_0_description') or ''
        meal_1_name = request.form.get('meal_1_name') or 'Vegetarian'
        meal_1_desc = request.form.get('meal_1_description') or ''

        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            # Ensure exactly two meal options; create or update
            meals = sorted(event.meal_options, key=lambda m: m.id)
            for i, (name, desc) in enumerate([(meal_0_name, meal_0_desc), (meal_1_name, meal_1_desc)]):
                if i < len(meals):
                    meals[i].name = name
                    meals[i].description = desc or None
                else:
                    db.session.add(MealOption(event_id=event.id, name=name, description=desc or None))
            db.session.commit()
            flash('Event updated successfully!')
            return redirect(url_for('admin.dashboard'))
        except ValueError:
            flash('Invalid date format.', 'error')

    return render_template('admin/event_form.html', event=event)

@bp.route('/events/<int:event_id>/cancel', methods=['POST'])
@admin_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = EventStatus.CANCELLED
    db.session.commit()
    flash(f'Event "{event.title}" has been cancelled.')
    return redirect(url_for('admin.dashboard'))

@bp.route('/orders')
@admin_required
def list_orders():
    event_id = request.args.get('event_id')
    
    query = Order.query
    if event_id and event_id != 'all':
        query = query.filter_by(event_id=event_id)
    
    orders = query.order_by(Order.created_at.desc()).all()
    events = Event.query.order_by(Event.date.desc()).all()
    
    return render_template('admin/orders.html', orders=orders, events=events, current_filter=event_id)


@bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Admin can mark an order as paid (from pending or processing)."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status != 'paid':
        flash('Invalid status.', 'error')
        return redirect(url_for('admin.list_orders', event_id=request.args.get('event_id')))
    if order.status not in (OrderStatus.PENDING, OrderStatus.PROCESSING):
        flash(f'Order #{order.id} cannot be changed to paid (current: {order.status.value}).', 'error')
        return redirect(url_for('admin.list_orders', event_id=request.args.get('event_id')))
    order.status = OrderStatus.PAID
    if not order.payment_reference:
        order.payment_reference = f"ADMIN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db.session.commit()
    flash(f'Order #{order.id} marked as paid. Customer will see it in My Orders.', 'success')
    return redirect(url_for('admin.list_orders', event_id=request.args.get('event_id')))

@bp.route('/orders/export')
@admin_required
def export_orders():
    event_id = request.args.get('event_id')
    
    # 1. Excel Export for "All Events"
    if not event_id or event_id == 'all':
        wb = Workbook()
        # Remove default sheet
        default_ws = wb.active
        wb.remove(default_ws)
        
        events = Event.query.order_by(Event.date.desc()).all()
        
        for event in events:
            # Create a sheet for each event, sanitize title length (limit 30 chars for Excel sheet names)
            sheet_title = "".join(c for c in event.title if c.isalnum() or c in (' ', '_', '-'))[:30]
            ws = wb.create_sheet(title=sheet_title)
            
            # Header
            ws.append(['Order ID', 'Date', 'Customer Name', 'Customer Tel', 'Meal', 'Amount', 'Admin Fee', 'Total', 'Status', 'Payment Method', 'Screenshot'])
            
            # Data
            orders = Order.query.filter_by(event_id=event.id).order_by(Order.created_at.desc()).all()
            for order in orders:
                ws.append([
                    order.id,
                    order.created_at.strftime('%Y-%m-%d %H:%M'),
                    order.user.name,
                    order.user.telephone,
                    order.meal_option.name,
                    order.amount,
                    order.admin_fee,
                    order.amount + order.admin_fee,
                    order.status.value,
                    order.payment_method or 'N/A',
                    order.payment_screenshot or ''
                ])
        
        out = BytesIO()
        wb.save(out)
        out.seek(0)
        
        return send_file(
            out, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, 
            download_name='orders_report_all_events.xlsx'
        )

    # 2. CSV Export for Single Event
    else:
        def generate():
            data = StringIO()
            w = csv.writer(data)
            
            # Write Header
            w.writerow(('Order ID', 'Date', 'Customer', 'Telephone', 'Event', 'Meal Option', 'Amount', 'Admin Fee', 'Total', 'Status', 'Payment Method', 'Screenshot'))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
            orders = Order.query.filter_by(event_id=event_id).order_by(Order.created_at.desc()).all()
            for order in orders:
                w.writerow((
                    order.id,
                    order.created_at.strftime('%Y-%m-%d %H:%M'),
                    order.user.name,
                    order.user.telephone,
                    order.event.title,
                    order.meal_option.name,
                    order.amount,
                    order.admin_fee,
                    order.amount + order.admin_fee,
                    order.status.value,
                    order.payment_method or 'N/A',
                    order.payment_screenshot or ''
                ))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

        response = Response(stream_with_context(generate()), mimetype='text/csv')
        response.headers.set('Content-Disposition', 'attachment', filename=f'orders_report_event_{event_id}.csv')
        return response

@bp.route('/touchngo/verify')
@admin_required
def touchngo_verifications():
    """List all pending Touch n Go payments for verification"""
    orders = Order.query.filter_by(
        status=OrderStatus.PROCESSING,
        payment_method='touchngo'
    ).order_by(Order.created_at.desc()).all()
    
    return render_template('admin/touchngo_verify.html', orders=orders)

@bp.route('/touchngo/verify/<int:order_id>', methods=['POST'])
@admin_required
def verify_touchngo(order_id):
    """Approve or reject a Touch n Go payment"""
    order = Order.query.get_or_404(order_id)
    action = request.form.get('action')
    
    if order.status != OrderStatus.PROCESSING or order.payment_method != 'touchngo':
        flash('Invalid order for verification.', 'error')
        return redirect(url_for('admin.touchngo_verifications'))
    
    if action == 'approve':
        order.status = OrderStatus.PAID
        order.payment_reference = f"TNG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        flash(f'Order #{order.id} approved successfully!', 'success')
    elif action == 'reject':
        order.status = OrderStatus.FAILED
        flash(f'Order #{order.id} rejected.', 'warning')
    else:
        flash('Invalid action.', 'error')
        return redirect(url_for('admin.touchngo_verifications'))
    
    db.session.commit()
    return redirect(url_for('admin.touchngo_verifications'))
