# app/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String)

    organisations = db.relationship('Organisation', secondary='user_organisation', back_populates='users')

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Organisation(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    users = db.relationship('User', secondary='user_organisation', back_populates='organisations')

user_organisation = db.Table('user_organisation',
    db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organisation_id', db.String, db.ForeignKey('organisation.id'), primary_key=True)
)
