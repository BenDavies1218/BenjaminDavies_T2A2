from init import db, ma
from marshmallow import fields


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reviews = db.relationship("Review", back_populates="user", cascade="all, delete")


class UserSchema(ma.Schema):
    reviews = fields.List(fields.Nested("ReviewSchema", exclude=["user"]))

    class Meta:
        fields = (
            "id",
            "name",
            "email",
            "password",
            "is_admin",
            "reviews",
        )


user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(many=True, exclude=["password"])
