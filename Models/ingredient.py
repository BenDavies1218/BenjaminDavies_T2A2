from init import db, ma
from marshmallow import fields
from Functions.Validation_functions import string_validation


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete"
    )


class IngredientSchema(ma.Schema):
    name = fields.String(required=True, validate=string_validation(max=50))

    class Meta:
        fields = ("id", "name")


ingredient_schema = IngredientSchema()
ingredients_schema = IngredientSchema(many=True)
