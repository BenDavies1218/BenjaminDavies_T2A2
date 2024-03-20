from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, And, Regexp


class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship(
        "RecipeAllergy", back_populates="allergy", cascade="all, delete"
    )


class AllergySchema(ma.Schema):
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


Allergy_schema = AllergySchema()
Allergies_schema = AllergySchema(many=True)
