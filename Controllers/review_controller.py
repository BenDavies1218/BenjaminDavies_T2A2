from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError, DataError
from flask_jwt_extended import jwt_required, get_jwt_identity
from psycopg2 import errorcodes
from Models.recipe import Recipe

from Functions.Decorator_functions import user_owner
from init import db
from Models.review import Review, review_schema, reviews_schema

review_bp = Blueprint("review", __name__, url_prefix="/review")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE
@review_bp.route("/<int:recipe_id>", methods=["POST"])
@jwt_required()
def create_review(recipe_id):
    try:
        body_data = review_schema.load(request.get_json())
        user_id = get_jwt_identity()
        recipe_owner = db.session.query(Recipe).filter_by(id=recipe_id).first()
        if user_id == str(recipe_owner.user_id):
            return {"error": f"you cant make a review for your own recipe!!"}, 400
        new_review = Review(
            details=body_data.get("details"),
            rating=body_data.get("rating"),
            user_id=user_id,
            recipe_id=recipe_id,
        )

        db.session.add(new_review)
        db.session.commit()

        return {
            "message": f"Review for recipe with id '{recipe_id}' succefully created"
        }, 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}
    except DataError as err:
        if err.orig.pgcode == errorcodes.ZERO_LENGTH_CHARACTER_STRING:
            return {
                "error": f"One or more fields are the wrong data type please refer to the schema"
            }


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@review_bp.route("/")
def get_all_reviews():
    reviews = db.select(Review)
    stmt = db.session.scalars(reviews)
    return reviews_schema.dump(stmt), 200


@review_bp.route("/<int:recipe_id>")
def get_review_by_recipe(recipe_id):
    highest = request.args.get("highest")
    newest = request.args.get("newest")

    query = db.session.query(Review).filter_by(recipe_id=recipe_id)

    if highest:
        query = query.order_by(Review.rating.desc())
    if newest:
        query = query.order_by(Review.created.desc())

    reviews = query.all()

    return reviews_schema.dump(reviews), 200


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


@review_bp.route("/<int:review_id>", methods=["PUT", "PATCH"])
@jwt_required()
@user_owner
def update_review(review_id):
    body_data = review_schema.load(request.get_json(), partial=True)

    review = db.session.query(Review).filter_by(id=review_id).first()

    review.details = body_data.get("details") or review.details
    review.rating = body_data.get("rating") or review.rating

    db.session.commit()
    return {"message": f"Review with id {review_id} successfully updated"}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@review_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
@user_owner
def delete_review(review_id):
    review = db.select(Review).filter_by(id=review_id).first()
    if not review:
        return {"error": f"Review with id {review_id} couldn't be found"}, 404
    db.session.delete(review)
    db.session.commit()
    return {"message": f"Review with id {review_id} succesfully deleted"}, 200
