from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # date = db.Column(db.DateTime(timezone=True), default=func.now())  # Optional, keep if needed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(255))  # Optional, stores filename
    filepath = db.Column(db.String(255))  # Stores filepath (local storage)
    shared_with = db.relationship('User', secondary='file_share', backref='shared_files')  # Many-to-Many relationship

    def __repr__(self):
        return f"<File {self.filename}>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    files = db.relationship('File')  # One-to-Many relationship
    is_admin = db.Column(db.Boolean, default=False)


# Association table for file sharing
file_share = db.Table('file_share',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
