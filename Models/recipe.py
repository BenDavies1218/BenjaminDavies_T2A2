from init import db, ma
from marshmallow import fields
from Functions.Validation_functions import string_validation, integer_validation
from sqlalchemy import DateTime
import datetime


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    difficulty = db.Column(db.Integer, nullable=True)
    serving_size = db.Column(db.Integer, nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="recipes_user_id_fkey"),
        nullable=False,
    )
    created = db.Column(DateTime, default=datetime.datetime.now)

    # Add foreign key relationships
    user = db.relationship("User", back_populates="recipes", cascade="all, delete")
    reviews = db.relationship(
        "Review",
        back_populates="recipe",
        foreign_keys="[Review.recipe_id]",
        cascade="all, delete",
    )
    ingredients = db.relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete"
    )
    allergies = db.relationship(
        "RecipeAllergy", back_populates="recipe", cascade="all, delete"
    )


class RecipeSchema(ma.Schema):
    title = fields.Str(required=True, validate=string_validation(max=100))
    difficulty = fields.Int(required=False, validate=integer_validation(max=10))
    serving_size = fields.Int(required=False, validate=integer_validation(max=32))
    instructions = fields.Str(
        required=True, validate=string_validation(max=500, all_char=True)
    )

    user = fields.Nested("UserSchema", only=("name", "email"))
    reviews = fields.List(
        fields.Nested("ReviewSchema", exclude=("id", "user.id", "recipe"))
    )
    ingredients = fields.List(
        fields.Nested(
            "RecipeIngredientSchema",
            exclude=("ingredient.id", "id"),
        )
    )
    allergies = fields.List(
        fields.Nested("RecipeAllergySchema", exclude=("id", "allergy.id"))
    )

    class Meta:
        fields = (
            "id",
            "title",
            "user",
            "reviews",
            "difficulty",
            "serving_size",
            "instructions",
            "ingredients",
            "allergies",
        )


recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
