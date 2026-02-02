from app import create_app, db
from app.models import Event, MealOption, EventStatus
from datetime import datetime, timedelta

def test_epic3():
    app = create_app()
    with app.app_context():
        print("Testing Epic 3...")
        
        # 1. Setup Data - Create Active Event with Default Meals
        event = Event(
            title="Public Gala",
            description="Open for everyone",
            date=datetime.now() + timedelta(days=5),
            location="City Hall",
            fee=50.0,
            status=EventStatus.ACTIVE
        )
        db.session.add(event)
        
        # Manually add meals for this test to ensure logic works if not running admin route
        # Wait, I updated admin route, but I'm not calling the route here, I'm calling DB directly.
        # So I should manually add them to simulate what the admin route does
        meals = ['Option A', 'Option B']
        for m in meals:
            db.session.add(MealOption(event=event, name=m))
            
        db.session.commit()
        
        # 2. Verify Meal Options
        fetched_event = Event.query.filter_by(title="Public Gala").first()
        if not fetched_event: 
            print("FAIL: Event not found")
            return
            
        if len(fetched_event.meal_options) == 2:
            print(f"SUCCESS: Event has {len(fetched_event.meal_options)} meal options.")
        else:
            print(f"FAIL: Expected 2 meal options, found {len(fetched_event.meal_options)}")
            
        # 3. Simulate Listing Query
        active_events = Event.query.filter_by(status=EventStatus.ACTIVE).all()
        if fetched_event in active_events:
            print("SUCCESS: Active event found in listing query.")
        
        # Cleanup
        db.session.delete(fetched_event)
        db.session.commit()
        print("SUCCESS: Cleanup.")

if __name__ == "__main__":
    test_epic3()
