from app import create_app, db
from app.models import Event, Order

def migrate_defaults():
    app = create_app()
    with app.app_context():
        print("Migrating defaults for existing data...")
        
        # Update Events where admin_fee is None
        events = Event.query.filter(Event.admin_fee == None).all()
        for e in events:
            e.admin_fee = 1.0
            print(f"Set admin_fee=1.0 for event: {e.title}")
            
        # Update Orders where admin_fee is None
        orders = Order.query.filter(Order.admin_fee == None).all()
        for o in orders:
            o.admin_fee = 0.0
            print(f"Set admin_fee=0.0 for order #{o.id}")
            
        # Update Orders where payment_method is None
        orders_no_method = Order.query.filter(Order.payment_method == None).all()
        for o in orders_no_method:
            o.payment_method = 'stripe' # Assume stripe for old orders
            print(f"Set payment_method='stripe' for order #{o.id}")
            
        db.session.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate_defaults()
