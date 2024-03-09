from datetime import datetime
from init import db, ma
from marshmallow import fields


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredient"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), nullable=False
    )
    amount = db.Column(db.String, nullable=True)

    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipes")


class RecipeIngredientSchema(ma.Schema):
    ingredient = fields.Nested("IngredientSchema", only=("id", "name"))

    class Meta:
        fields = ("id", "amount", "ingredient")


recipe_ingredient_schema = RecipeIngredientSchema()
recipes_ingredient_schema = RecipeIngredientSchema(many=True)
