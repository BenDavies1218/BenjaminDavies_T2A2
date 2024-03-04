from datetime import datetime
from init import db, ma
from marshmallow import fields


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    created = db.Column(db.DateTime(timezone=True), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="reviews")


class ReviewSchema(ma.Schema):

    user = fields.Nested("UserSchema", only=["name", "email"])

    class Meta:
        fields = (
            "id",
            "details",
            "rating",
            "created",
            "user",
        )


review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
