from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Removed data column for file uploads
    # date = db.Column(db.DateTime(timezone=True), default=func.now())  # Optional, keep if needed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(255))  # Optional, stores filename
    filepath = db.Column(db.String(255))  # Stores filepath (local storage)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    files = db.relationship('File')