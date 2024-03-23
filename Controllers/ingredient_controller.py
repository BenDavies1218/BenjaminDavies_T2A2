from sqlalchemy import func, text
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from psycopg2 import errorcodes
from Functions.Decorator_functions import authorise_as_admin, any_user
from Models.recipe_ingredients import RecipeIngredient

from init import db
from Models.ingredient import Ingredient, ingredient_schema, ingredients_schema

ingredient_bp = Blueprint("ingredient", __name__, url_prefix="/ingredient")

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


@ingredient_bp.route("/", methods=["POST"])
@jwt_required()
@any_user
def create_ingredient():
    try:
        body_data = ingredient_schema.load(request.get_json())

        # Create a new ingredient instance
        new_ingredient = Ingredient(name=body_data.get("name"))
        db.session.add(new_ingredient)
        db.session.commit()
        # send msg back to user
        return {
            "message": f"new ingredient {new_ingredient.name} succefully created"
        }, 200

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"Ingredient {new_ingredient.name} already exists"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@ingredient_bp.route("/")
@jwt_required()
@any_user
def get_ingredient():
    # select all of the Ingredients in the database
    all_ingredients = db.select(Ingredient)
    stmt = db.session.scalars(all_ingredients)

    # checks it search parameter is true
    search = request.args.get("search")
    if search:
        # query the database for ingredient names that are like the query parameter
        search_ingredient = (
            db.session.query(Ingredient)
            .filter(func.lower(Ingredient.name).ilike(f"%{search.lower()}%"))
            .all()
        )
        # if ingredients with similar name exist then we return them to the user
        if search_ingredient:
            return ingredients_schema.dump(search_ingredient), 200

        # if there no ingredients then return msg no ingredients match that name
        else:
            return {"Error": f"No Ingredients with the name '{search}' found."}, 404
    return ingredients_schema.dump(stmt), 200


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


# this is a very powerful route as it has the ability to change the ingredient on every recipe, possible uses may be if you want to change the all ingredients with the name "eggs" to "chickens eggs". Only administators can use this endpoint
@ingredient_bp.route("/<int:ing_id>", methods=["PUT", "PATCH"])
@jwt_required()
@authorise_as_admin
def update_ingredient(ing_id):
    try:
        body_data = ingredient_schema.load(request.get_json(), partial=True)
        # Query Ingredients fitlering by ingredient id
        stmt = db.select(Ingredient).filter_by(id=ing_id)
        ingredient = db.session.scalar(stmt)

        # updates the name
        ingredient.name = body_data.get("name") or ingredient.name
        db.session.commit()
        return {"message": f"Ingredient with id {ing_id} successfully updated"}, 200
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@ingredient_bp.route("/", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient():
    try:
        # create a query that selects all the ingredients in the database that dont exist in the recipe_ingredient table
        sql_query = """
            DELETE FROM ingredient
            WHERE id NOT IN (SELECT DISTINCT ingredient_id FROM recipe_ingredient);
        """
        # excute query
        db.session.execute(text(sql_query))
        db.session.commit()

        # return msg to user that all ingredients have been deleted
        return {
            "message": "All ingredients without relations successfully deleted"
        }, 204

    except IntegrityError:
        # If the query encounters an error return this
        return {"error": "An integrity error occurred"}, 400


@ingredient_bp.route("/<int:ing_id>", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient_by_id(ing_id):
    # query the database for all of the recipe ingredients that match the target id
    existing_recipe = (
        db.session.query(RecipeIngredient).filter_by(ingredient_id=ing_id).first()
    )
    # if there are no recipes with our target ingredient
    if existing_recipe is None:

        # query Ingredient for ingredient that matches the target id
        ingredient = db.session.query(Ingredient).get(ing_id)
        # if the ingredient exists then we delete it
        if ingredient:
            db.session.delete(ingredient)
            db.session.commit()
            # msg for successful deletion
            return {"message": f"Ingredient with id {ing_id} successfully deleted"}, 204
        # error with the Ingredient query
        else:
            return {"error": f"Ingredient with id {ing_id} not found"}, 404

    # if the target ingredient has relations than we cant delete it because that will cause a foriegn key null error and crash the database
    else:
        return {
            "error": f"Couldn't delete ingredient with ID {ing_id} as it has relations with 1 or more recipes"
        }, 400
