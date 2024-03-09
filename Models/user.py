from init import db, ma
from marshmallow import fields


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime(timezone=True), nullable=False)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")
    recipes = db.relationship("Recipe", back_populates="user", cascade="all, delete")


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "is_admin", "created")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
