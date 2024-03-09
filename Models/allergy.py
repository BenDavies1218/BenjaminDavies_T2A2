from datetime import datetime
from init import db, ma
from marshmallow import fields


class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    recipes = db.relationship("RecipeAllergy", back_populates="allergy")


class AllergySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")


recipe_Allergy_schema = AllergySchema()
recipes_Allergy_schema = AllergySchema(many=True)
