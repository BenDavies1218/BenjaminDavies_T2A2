from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, And, Regexp


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete"
    )


class IngredientSchema(ma.Schema):
    name = fields.String(
        required=True,
        validate=And(
            Length(min=2, error="Name must be at least 2 characters long"),
            Regexp(
                "^[a-zA-Z0-9 ]+$",
                error="Title can only contain alphanumeric characters",
            ),
        ),
    )

    class Meta:
        fields = ("id", "name")


ingredient_schema = IngredientSchema()
ingredients_schema = IngredientSchema(many=True)
