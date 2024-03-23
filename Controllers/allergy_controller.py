from sqlalchemy import func, text
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from psycopg2 import errorcodes
from Functions.Decorator_functions import authorise_as_admin, any_user
from Models.recipe_allergies import RecipeAllergy

from init import db
from Models.allergy import Allergy, allergy_schema, allergies_schema

allergy_bp = Blueprint("allergy", __name__, url_prefix="/allergy")

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


@allergy_bp.route("/", methods=["POST"])
@jwt_required()
@any_user
def create_allergy():
    try:
        body_data = allergy_schema.load(request.get_json())
        # Create a new instance of the allergy
        new_allergy = Allergy(name=body_data.get("name"))
        db.session.add(new_allergy)
        db.session.commit()
        # return succesfully creation msg
        return {"message": f"new allergy {new_allergy.name} succefully created"}, 200

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"allergy {new_allergy.name} already exists"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@allergy_bp.route("/")
@jwt_required()
@any_user
def get_ingredient():
    # query Allergy and select all allergies
    all_allergies = db.select(Allergy)
    stmt = db.session.scalars(all_allergies)

    # check if the search query parameter is true
    search = request.args.get("search")
    if search:
        # query the Allergy table for allergy names that are similar to the query parameter
        search_allergy = (
            db.session.query(Allergy)
            .filter(func.lower(Allergy.name).ilike(f"%{search.lower()}%"))
            .all()
        )
        # if the query returns allergies then return them to the user
        if search_allergy:
            return allergies_schema.dump(search_allergy), 200

        # error msg didn't find any allergies with a similar name to the query parameter
        else:
            return {"Error": f"No Allergies with the name '{search}' found."}, 404
    # return all of the allergies if theres no query parameter in the request
    return allergies_schema.dump(stmt)


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


# this is a very powerful route as it has the ability to change the allergy on every recipe, possible uses may be if you want to change the all allergy with the name "Dairy" to "Lactose". Only administators can use this endpoint
@allergy_bp.route("/<int:all_id>", methods=["PUT", "PATCH"])
@jwt_required()
@authorise_as_admin
def update_ingredient(all_id):
    try:
        body_data = allergy_schema.load(request.get_json(), partial=True)

        # Query Allergy and select the allergy with the target ID
        stmt = db.select(Allergy).filter_by(id=all_id).first()
        allergy = db.session.scalar(stmt)

        if not stmt:
            return {"error": "allergy with id {all_id} couldn't be found"}, 404

        # update the name
        allergy.name = body_data.get("name") or allergy.name
        db.session.commit()
        # return msg to the user that it was successful update
        return {"message": f"Allergy with id {all_id} successfully updated"}, 200
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@allergy_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient():
    # create a query that selects all the allergies in the database that dont exist in the recipe_allergy table
    try:
        sql_query = """
            DELETE FROM allergy
            WHERE id NOT IN (SELECT DISTINCT allergy_id FROM recipe_allergy);
        """
        # execute query
        db.session.execute(text(sql_query))
        db.session.commit()
        # return successful msg to user
        return {"message": "Allergies without any relations successfully deleted"}, 200

    except IntegrityError:
        # if there is a problem with the query
        return {"error": "A query error occurred"}, 500


@allergy_bp.route("/delete/<int:all_id>", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient_by_id(all_id):
    # query the database for all of the recipe_allergies that match the target id
    existing_recipe = (
        db.session.query(RecipeAllergy).filter_by(allergy_id=all_id).first()
    )
    if existing_recipe is None:
        # query Allergy for Allergy that matches the target id
        allergy = db.session.query(Allergy).get(all_id)
        # If allergy exists then we delete it
        if allergy:
            db.session.delete(allergy)
            db.session.commit()
            return {"message": f"Allergy with id {all_id} successfully deleted"}, 200

        # Return error couldn't find allergy
        else:
            return {"error": f"Allergy with id {all_id} not found"}, 400
    else:
        # if the target allergy has relations than we cant delete it because that will cause a foriegn key null error and crash the database
        return {
            "error": f"Couldn't delete ingredient with ID {all_id} as it has relations with 1 or more recipes"
        }, 403
