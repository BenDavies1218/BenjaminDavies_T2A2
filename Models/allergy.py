from init import db, ma
from marshmallow import fields
from Functions.Validation_functions import string_validation


class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True)
    recipes = db.relationship(
        "RecipeAllergy", back_populates="allergy", cascade="all, delete"
    )


class AllergySchema(ma.Schema):
    name = fields.String(required=True, validate=string_validation(max=25))

    class Meta:
        fields = ("id", "name")


allergy_schema = AllergySchema()
allergies_schema = AllergySchema(many=True)
