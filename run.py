from app import create_app, db
from app.models import User, Event, MealOption, Order

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Event': Event, 'MealOption': MealOption, 'Order': Order}

if __name__ == '__main__':
    app.run(debug=True, port=5555)
