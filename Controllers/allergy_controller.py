from sqlalchemy import func, text
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from psycopg2 import errorcodes
from Functions.Decorator_functions import authorise_as_admin
from Models.recipe_ingredients import RecipeIngredient

from init import db
from Models.allergy import Allergy, allergy_schema, allergies_schema

allergy_bp = Blueprint("allergy", __name__, url_prefix="/allergy")

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


@allergy_bp.route("/", methods=["POST"])
def create_allergy():
    try:
        body_data = allergy_schema.load(request.get_json())
        new_allergy = Allergy(name=body_data.get("name"))
        db.session.add(new_allergy)
        db.session.commit()
        return {"message": f"new ingredient {new_allergy.name} succefully created"}

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"Ingredient {new_allergy.name} already exists"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@allergy_bp.route("/")
def get_ingredient():
    all_allergies = db.select(Allergy)
    stmt = db.session.scalars(all_allergies)
    search = request.args.get("search")
    if search:
        search_allergy = (
            db.session.query(Allergy)
            .filter(func.lower(Allergy.name).ilike(f"%{search.lower()}%"))
            .all()
        )
        if search_allergy:
            return Allergies_schema.dump(search_allergy), 200
        else:
            return {"Error": f"No Allergies with the name '{search}' found."}, 404
    return Allergies_schema.dump(stmt)


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


# this is a very powerful route as it has the ability to change the ingredient on every recipe, possible uses may be if you want to change the all ingredients with the name "eggs" to "chickens eggs". Only administators can use this endpoint
@allergy_bp.route("/<int:all_id>", methods=["PUT", "PATCH"])
@jwt_required()
@authorise_as_admin
def update_ingredient(all_id):
    try:
        body_data = Allergy_schema.load(request.get_json(), partial=True)
        stmt = db.select(Allergy).filter_by(id=all_id)
        ingredient = db.session.scalar(stmt)
        ingredient.name = body_data.get("name") or ingredient.name
        db.session.commit()
        return {"message": f"Ingredient with id {all_id} successfully updated"}
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@allergy_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient():
    try:
        sql_query = """
            DELETE FROM allergy
            WHERE id NOT IN (SELECT DISTINCT allergy_id FROM recipe_allergy);
        """
        db.session.execute(text(sql_query))
        db.session.commit()
        return {"message": "Allergies without relations successfully deleted"}
    except IntegrityError:
        # if there is a problem with the query
        return {"error": "A query error occurred please try again"}


@allergy_bp.route("/delete/<int:all_id>", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient_by_id(all_id):
    if all_id:
        existing_recipe = (
            db.session.query(RecipeIngredient).filter_by(ingredient_id=all_id).first()
        )
        if existing_recipe is None:
            ingredient = db.session.query(Allergy).get(
                all_id
            )  # Use .get() to retrieve the ingredient by ID
            if ingredient:
                db.session.delete(ingredient)
                db.session.commit()
                return {"message": f"Ingredient with id {all_id} successfully deleted"}
            else:
                return {"error": f"Ingredient with id {all_id} not found"}
        else:
            return {
                "error": f"Couldn't delete ingredient with ID {all_id} as it has relations with 1 or more recipes"
            }
