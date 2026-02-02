from flask import Blueprint, render_template, abort
from app.models import Event, EventStatus, MealOption

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/', methods=['GET'])
def list_events():
    # Show active events, sorted by date
    events = Event.query.filter_by(status=EventStatus.ACTIVE)\
        .order_by(Event.date.asc()).all()
    return render_template('events/list.html', events=events)

@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.status == EventStatus.CANCELLED:
        # Optionally show but mark as cancelled, or generic 404?
        # Requirement says "Cancelled events hidden or labeled".
        pass
    meal_menu_descriptions = [
        {"id": m.id, "description": m.description or ""}
        for m in event.meal_options
    ]
    return render_template(
        'events/detail.html',
        event=event,
        meal_menu_descriptions=meal_menu_descriptions,
    )
