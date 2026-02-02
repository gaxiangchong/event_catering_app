from app import create_app, db
from app.models import User, Event, EventStatus
import sys
from datetime import datetime

app = create_app()

def test_admin_flow():
    print("Testing Admin Flow...")
    with app.app_context():
        # 1. Verify Admin Exists
        admin = User.query.filter_by(telephone="0000000000").first()
        if not admin or not admin.is_admin:
            print("FAILURE: Admin user not found or not is_admin.")
            sys.exit(1)
        print("SUCCESS: Admin user verified.")

        # 2. Test Event Creation (Simulate Logic)
        new_event = Event(
            title="Test Event",
            description="A test event",
            date=datetime.now(),
            location="Test Loc",
            fee=100.0,
            capacity=50,
            status=EventStatus.ACTIVE
        )
        db.session.add(new_event)
        db.session.commit()
        
        saved_event = Event.query.filter_by(title="Test Event").first()
        if saved_event:
            print(f"SUCCESS: Event '{saved_event.title}' created.")
        else:
            print("FAILURE: Event creation failed.")
            sys.exit(1)
            
        # 3. Test Event Cancel
        saved_event.status = EventStatus.CANCELLED
        db.session.commit()
        
        cancelled = Event.query.get(saved_event.id)
        if cancelled.status == EventStatus.CANCELLED:
            print("SUCCESS: Event cancelled.")
        else:
            print("FAILURE: Event cancellation failed.")
            sys.exit(1)

        # Cleanup
        db.session.delete(saved_event)
        db.session.commit()
        print("SUCCESS: Cleanup done.")

if __name__ == "__main__":
    try:
        test_admin_flow()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
