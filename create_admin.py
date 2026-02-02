from app import create_app, db
from app.models import User
import sys

def create_admin(name, tel):
    app = create_app()
    with app.app_context():
        # Check if exists
        u = User.query.filter_by(telephone=tel).first()
        if u:
            print(f"User with tel {tel} already exists.")
            if not u.is_admin:
                u.is_admin = True
                db.session.commit()
                print(f"Promoted {name} to Admin.")
            else:
                print("User is already Admin.")
        else:
            admin = User(name=name, telephone=tel, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print(f"Created new Admin user: {name} ({tel})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <Name> <Tel>")
        # Default for dev convenience if no args
        create_admin("Super Admin", "0000000000")
    else:
        create_admin(sys.argv[1], sys.argv[2])
