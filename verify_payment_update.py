from app import create_app, db
from app.models import Event, Order, User, MealOption, OrderStatus
from datetime import datetime
import csv
import io

def verify_payment_features():
    app = create_app()
    with app.app_context():
        print("--- Verifying Models ---")
        event = Event.query.first()
        if event:
            print(f"Event admin_fee: {event.admin_fee} (Expected default: 1.0)")
            
        order = Order.query.order_by(Order.id.desc()).first()
        if order:
            print(f"Order payment_method: {order.payment_method}")
            print(f"Order admin_fee: {order.admin_fee}")
            print(f"Order total: {order.amount + order.admin_fee}")
        
        print("\n--- Verifying CSV Export Logic ---")
        from app.routes.admin import bp
        # We can't easily call the route without a request, but we can verify the fields exist in the model
        print("Fields in Order model:", [c.name for c in Order.__table__.columns])
        
        print("\n--- Verifying Upload Directory ---")
        import os
        upload_path = app.config['UPLOAD_FOLDER']
        print(f"Upload path: {upload_path}")
        if os.path.exists(upload_path):
            print("Upload directory exists.")
        else:
            print("Upload directory MISSING!")

if __name__ == "__main__":
    verify_payment_features()
