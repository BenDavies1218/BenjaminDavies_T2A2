from datetime import datetime
from init import db, ma
from marshmallow import fields


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("recipe_ingredients.id"), nullable=False)
    difficulty = db.Column(db.Integer, nullable=True)
    serving_size = db.Column(db.Integer, nullable=True)
    instructions = db.Column(db.Text(500), nullable=False)
    allergy_id = db.Column(db.Integer, db.ForeignKey("recipe_allergies") nullable=True)
    created = db.Column(db.DateTime(timezone=True), nullable=False)

    user = db.relationship("User", back_populates="recipes")
    reviews = db.relationship("Review", back_populates="recipes")
    ingredients = db.relationship("Recipe_ingredients", back_populates="recipes")
    allergies = db.relationship("Recipe_allergies", back_populates="recipes")

class RecipeSchema(ma.Schema):

    user = fields.Nested("UserSchema", only=["name", "email"])
    reviews = fields.List(fields.Nested("ReviewSchema", exclude=["user"]))
    ingredients = fields.List(fields.Nested("Recipe_IngredientsSchema", exclude=["recipe_id"]))
    allergies = ingredients = fields.List(fields.Nested("Recipe_AllergieSchema", exclude=["recipe_id"]))



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
