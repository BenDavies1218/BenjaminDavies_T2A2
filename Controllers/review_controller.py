from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError, DataError
from flask_jwt_extended import jwt_required, get_jwt_identity
from psycopg2 import errorcodes
from Models.recipe import Recipe

from Functions.Decorator_functions import user_owner, any_user
from init import db
from Models.review import Review, review_schema, reviews_schema

review_bp = Blueprint("review", __name__, url_prefix="/review")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE
@review_bp.route("/<int:recipe_id>", methods=["POST"])
@jwt_required()
@any_user
def create_review(recipe_id):
    try:
        body_data = review_schema.load(request.get_json())
        user_id = get_jwt_identity()
        # query database for recipe we target id
        recipe_owner = db.session.query(Recipe).filter_by(id=recipe_id).first()

        if not recipe_owner:
            return {"error": f"recipe with id {recipe_id} could not be found"}

        # check if user id is the owner of the recipe, converting to a string because when we created the access token we speficied is was a type(str)
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
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
    except DataError as err:
        if err.orig.pgcode == errorcodes.ZERO_LENGTH_CHARACTER_STRING:
            return {
                "error": f"One or more fields are the wrong data type please refer to the schema"
            }, 400


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@review_bp.route("/")
@jwt_required()
@any_user
def get_all_reviews():
    # query database for all of the reviews and return them to the user
    reviews = db.select(Review)
    stmt = db.session.scalars(reviews)
    return reviews_schema.dump(stmt), 200


@review_bp.route("/<int:recipe_id>")
@jwt_required()
@any_user
def get_review_by_recipe(recipe_id):
    # check for query parameters
    highest = request.args.get("highest")
    newest = request.args.get("newest")

    # query database to find the target recipe return all of the recipes
    query = db.session.query(Review).filter_by(recipe_id=recipe_id).all()

    if not query:
        return {"error": f"recipe with id {recipe_id} couldn't be found"}, 404

    # check if the highest parameter exists
    if highest:
        # creating the logic to order the reviews from highest to lowest rating
        query = query.order_by(Review.rating.desc())

    # check if newest exists
    if newest:
        # creating logic to order the data from newest to oldest
        query = query.order_by(Review.created.desc())

    # declares that the reviews in equal to all of the reviews we retrieved from the database
    reviews = query.all()

    # return the reviews to the user
    return reviews_schema.dump(reviews), 200


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


@review_bp.route("/<int:review_id>", methods=["PUT", "PATCH"])
@jwt_required()
@user_owner
def update_review(review_id):
    body_data = review_schema.load(request.get_json(), partial=True)

    # Query database to update the target review
    review = db.session.query(Review).filter_by(id=review_id).first()

    # if we cant find the review by id
    if not review:
        return {"error": f"Review with id {review_id} couldn't be found"}, 404
    review.details = body_data.get("details") or review.details
    review.rating = body_data.get("rating") or review.rating

    db.session.commit()
    return {"message": f"Review with id {review_id} successfully updated"}, 200


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@review_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
@user_owner
def delete_review(review_id):
    # Query database to find the target review
    review = db.select(Review).filter_by(id=review_id).first()

    # if the review doesn't exist send an error to the user
    if not review:
        return {"error": f"Review with id {review_id} couldn't be found"}, 404

    # delete the review
    db.session.delete(review)
    db.session.commit()

    # return message to the user
    return {"message": f"Review with id {review_id} succesfully deleted"}, 200
