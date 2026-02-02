from app import db
from datetime import datetime
from enum import Enum
from flask_login import UserMixin

class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    FAILED = 'failed'
    PROCESSING = 'processing'

class EventStatus(Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    telephone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.telephone}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    fee = db.Column(db.Float, nullable=False)
    admin_fee = db.Column(db.Float, default=1.0)
    capacity = db.Column(db.Integer)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.ACTIVE)
    image_url = db.Column(db.String(300))
    
    meal_options = db.relationship('MealOption', backref='event', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='event', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.title}>'

class MealOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # menu description

    def __repr__(self):
        return f'<MealOption {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    meal_option_id = db.Column(db.Integer, db.ForeignKey('meal_option.id'))
    amount = db.Column(db.Float, nullable=False)
    admin_fee = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_screenshot = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meal_option = db.relationship('MealOption')

    def __repr__(self):
        return f'<Order {self.id}>'
