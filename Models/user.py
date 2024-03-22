from init import db, ma
from sqlalchemy import DateTime
import datetime
from marshmallow import fields
from Functions.Validation_functions import string_validation, password_validation


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created = db.Column(DateTime, default=datetime.datetime.now)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")
    recipes = db.relationship("Recipe", back_populates="user", cascade="all, delete")


class UserSchema(ma.Schema):
    name = fields.Str(required=False, validate=string_validation(max=100))
    email = fields.Str(required=True, validate=string_validation(email=True, max=200))
    password = fields.Str(required=True, validate=password_validation())
    is_admin = fields.Bool()

    class Meta:
        fields = ("id", "name", "email", "password", "is_admin", "created")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
