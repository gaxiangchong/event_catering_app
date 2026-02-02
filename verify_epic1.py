from app import create_app, db
from app.models import User
import sys

app = create_app()

def test_user_creation():
    print("Testing User Creation...")
    with app.app_context():
        # Clean up if exists
        u = User.query.filter_by(telephone="999888777").first()
        if u:
            db.session.delete(u)
            db.session.commit()
        
        # Create
        new_user = User(name="Test User", telephone="999888777")
        db.session.add(new_user)
        db.session.commit()
        
        # Verify
        retrieved = User.query.filter_by(telephone="999888777").first()
        if retrieved and retrieved.name == "Test User":
            print("SUCCESS: User created and retrieved.")
        else:
            print("FAILURE: User not found or name mismatch.")
            sys.exit(1)

        # Clean up
        db.session.delete(retrieved)
        db.session.commit()
        print("SUCCESS: Cleaned up.")

if __name__ == "__main__":
    try:
        test_user_creation()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
