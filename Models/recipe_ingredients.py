from init import db, ma
from marshmallow import fields
from Functions.Validation_functions import string_validation


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredient"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), nullable=False
    )
    amount = db.Column(db.String(50), nullable=False)

    recipe = db.relationship(
        "Recipe", back_populates="ingredients", cascade="all, delete"
    )
    ingredient = db.relationship(
        "Ingredient", back_populates="recipes", cascade="all, delete"
    )


class RecipeIngredientSchema(ma.Schema):
    recipe_id = fields.Int(required=True)
    ingredient_id = fields.Int(required=True)
    amount = fields.Str(
        required=True, validate=string_validation(all_char=True, max=50, min=1)
    )
    ingredient = fields.Nested("IngredientSchema", only=("id", "name"))

    class Meta:
        fields = ("id", "ingredient", "amount")


recipe_ingredient_schema = RecipeIngredientSchema()
recipes_ingredient_schema = RecipeIngredientSchema(many=True)
