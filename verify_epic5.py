from app import create_app, db
from app.models import User, Event, MealOption, Order, OrderStatus, EventStatus
from datetime import datetime, timedelta

def test_epic5():
    app = create_app()
    with app.app_context():
        print("Testing Epic 5: History & Receipt...")
        
        # 1. Setup User
        user = User.query.filter_by(telephone="0000000000").first()
        if not user:
            user = User(name="Test User E5", telephone="555555555")
            db.session.add(user)
            db.session.commit()
            
        # 2. Creating Events and Orders
        event1 = Event(title="Past Event", date=datetime.now() - timedelta(days=1), fee=10.0, status=EventStatus.COMPLETED)
        event2 = Event(title="Future Event", date=datetime.now() + timedelta(days=1), fee=20.0, status=EventStatus.ACTIVE)
        db.session.add_all([event1, event2])
        db.session.flush()
        
        meal1 = MealOption(event_id=event1.id, name="Meal A")
        meal2 = MealOption(event_id=event2.id, name="Meal B")
        db.session.add_all([meal1, meal2])
        db.session.commit()
        
        # Order 1 (PAID, Past)
        order1 = Order(
            user_id=user.id,
            event_id=event1.id,
            meal_option_id=meal1.id,
            amount=10.0,
            status=OrderStatus.PAID,
            payment_reference="REF-PAST"
        )
        
        # Order 2 (PENDING, Future)
        order2 = Order(
            user_id=user.id,
            event_id=event2.id,
            meal_option_id=meal2.id,
            amount=20.0,
            status=OrderStatus.PENDING
        )
        
        db.session.add_all([order1, order2])
        db.session.commit()
        
        # 3. Verify Order List Logic
        # "orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()"
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
        
        if len(orders) >= 2:
            print(f"SUCCESS: Retrieved {len(orders)} orders.")
        else:
            print(f"FAILURE: Expected at least 2 orders, got {len(orders)}")
            
        # 4. Verify Receipt Details
        receipt = Order.query.get(order1.id)
        if receipt.payment_reference == "REF-PAST" and receipt.status == OrderStatus.PAID:
            print("SUCCESS: Paid receipt details verification passed.")
        else:
            print("FAILURE: Receipt details mismatch.")

        # Cleanup
        db.session.delete(order1)
        db.session.delete(order2)
        db.session.delete(event1)
        db.session.delete(event2)
        if user.telephone == "555555555":
            db.session.delete(user)
        db.session.commit()
        print("SUCCESS: Cleanup done.")

if __name__ == "__main__":
    test_epic5()
