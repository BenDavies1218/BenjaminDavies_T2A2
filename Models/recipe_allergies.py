from init import db, ma
from marshmallow import fields


class RecipeAllergy(db.Model):
    __tablename__ = "recipe_allergy"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    allergy_id = db.Column(db.Integer, db.ForeignKey("allergy.id"), nullable=False)

    recipe = db.relationship("Recipe", back_populates="allergies")
    allergy = db.relationship(
        "Allergy", back_populates="recipes", cascade="all, delete"
    )


class RecipeAllergySchema(ma.Schema):
    allergy = fields.Nested("AllergySchema", only=("id", "name"))

    class Meta:
        fields = ("id", "allergy")


recipe_allergies_schema = RecipeAllergySchema()
recipes_allergies_schema = RecipeAllergySchema(many=True)
