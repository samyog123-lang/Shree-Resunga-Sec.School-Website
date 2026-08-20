from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student / teacher / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), default='default.png')

    def __repr__(self):
        return f"<User {self.email}>"


class StudentRegistration(db.Model):
    __tablename__ = "student_registrations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, index=True)
    address = db.Column(db.String(300), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    applying_class = db.Column(db.String(50), nullable=False)
    previous_batch_year = db.Column(db.Integer, nullable=False)
    certificate_filename = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default="pending")
    payment_reference = db.Column(db.String(150))
    transaction_uuid = db.Column(db.String(120), unique=True)
    amount_paid = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StudentRegistration {self.name} - {self.applying_class} - {self.payment_status}>"
