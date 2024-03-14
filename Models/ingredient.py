from init import db, ma
from marshmallow import fields


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete"
    )


class IngredientSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")


recipe_ingredient_schema = IngredientSchema()
recipes_ingredients_schema = IngredientSchema(many=True)
