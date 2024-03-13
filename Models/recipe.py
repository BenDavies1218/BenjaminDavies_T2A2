from init import db, ma
from marshmallow import fields
from sqlalchemy import DateTime
import datetime
from Models.ingredient import IngredientSchema


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)
    serving_size = db.Column(db.Integer, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="recipes_user_id_fkey"),
        nullable=False,
    )
    review_id = db.Column(
        db.Integer,
        db.ForeignKey("reviews.id", name="recipes_review_id_fkey"),
        nullable=True,
    )
    created = db.Column(DateTime, default=datetime.datetime.utcnow)

    # Add foreign key relationships
    user = db.relationship("User", back_populates="recipes")
    reviews = db.relationship(
        "Review", back_populates="recipe", foreign_keys="[Review.recipe_id]"
    )
    ingredients = db.relationship("RecipeIngredient", back_populates="recipe")
    allergies = db.relationship("RecipeAllergy", back_populates="recipe")


class RecipeSchema(ma.Schema):
    # Adjust relationships in the schema
    user = fields.Nested("UserSchema", only=("name", "email"))
    reviews = fields.List(fields.Nested("ReviewSchema", exclude=("id", "user.id")))
    ingredients = fields.List(
        fields.Nested("RecipeIngredientSchema", only=("amount", "ingredient.name"))
    )
    allergies = fields.List(
        fields.Nested("RecipeAllergySchema", only=("allergy", "allergy.name"))
    )

    class Meta:
        fields = (
            "id",
            "title",
            "user",
            "reviews",
            "ingredients",
            "difficulty",
            "serving_size",
            "instructions",
            "allergies",
            "created",
        )


recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
