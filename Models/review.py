from init import db, ma
from marshmallow import fields
from sqlalchemy import DateTime
import datetime
from Functions.Validation_functions import string_validation, integer_validation


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created = db.Column(DateTime, default=datetime.datetime.now)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="reviews", cascade="all, delete")
    recipe = db.relationship("Recipe", back_populates="reviews")


# I created my own function to handle validation
class ReviewSchema(ma.Schema):
    details = fields.Str(
        required=True, validate=string_validation(max=500, all_char=True)
    )
    rating = fields.Int(required=True, validate=integer_validation(max=100))

    user = fields.Nested("UserSchema", only=("name", "email"))
    recipe = fields.Nested("RecipeSchema", only=("title", "id"))

    class Meta:
        fields = ("id", "details", "rating", "created", "user", "recipe")


review_schema = ReviewSchema(exclude=["recipe.id", "id"])
reviews_schema = ReviewSchema(many=True, exclude=["recipe.id", "id"])
