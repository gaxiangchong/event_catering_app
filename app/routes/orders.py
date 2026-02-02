from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import Order, OrderStatus

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/', methods=['GET'])
@login_required
def list_orders():
    # Fetch orders for current user, sorted by date desc
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()
    return render_template('orders/list.html', orders=orders)

@bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    # Security check: User can only view their own orders
    if order.user_id != current_user.id:
        abort(403)
        
    return render_template('orders/detail.html', order=order)
