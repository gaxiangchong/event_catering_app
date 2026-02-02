from app import create_app, db
from app.models import Event, Order, MealOption
import sqlalchemy

app = create_app()

def fix_db():
    with app.app_context():
        print("Cleaning up database...")
        # Delete all data from tables that might have bad enums
        try:
            num_orders = db.session.query(Order).delete()
            num_meals = db.session.query(MealOption).delete()
            num_events = db.session.query(Event).delete()
            db.session.commit()
            print(f"Deleted {num_orders} orders, {num_meals} meals, {num_events} events.")
            print("Database cleaned. You can now restart the app.")
        except Exception as e:
            print(f"Error cleaning DB: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_db()
