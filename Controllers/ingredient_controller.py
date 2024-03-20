from sqlalchemy import func, text
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from psycopg2 import errorcodes
from Functions.Decorator_functions import authorise_as_admin
from Models.recipe_ingredients import RecipeIngredient

from init import db
from Models.ingredient import Ingredient, ingredient_schema, ingredients_schema

ingredient_bp = Blueprint("ingredient", __name__, url_prefix="/ingredient")

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


@ingredient_bp.route("/", methods=["POST"])
def create_ingredient():
    try:
        body_data = ingredient_schema.load(request.get_json())
        new_ingredient = Ingredient(name=body_data.get("name"))
        db.session.add(new_ingredient)
        db.session.commit()
        return {"message": f"new ingredient {new_ingredient.name} succefully created"}

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"Ingredient {new_ingredient.name} already exists"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@ingredient_bp.route("/")
def get_ingredient():
    all_ingredients = db.select(Ingredient)
    stmt = db.session.scalars(all_ingredients)
    search = request.args.get("search")
    if search:
        search_ingredient = (
            db.session.query(Ingredient)
            .filter(func.lower(Ingredient.name).ilike(f"%{search.lower()}%"))
            .all()
        )
        if search_ingredient:
            return ingredients_schema.dump(search_ingredient), 200
        else:
            return {"Error": f"No Ingredients with the name '{search}' found."}, 404
    return ingredients_schema.dump(stmt)


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
        stmt = db.select(Ingredient).filter_by(id=ing_id)
        ingredient = db.session.scalar(stmt)
        ingredient.name = body_data.get("name") or ingredient.name
        db.session.commit()
        return {"message": f"Ingredient with id {ing_id} successfully updated"}
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@ingredient_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient():
    try:
        sql_query = """
            DELETE FROM ingredient
            WHERE id NOT IN (SELECT DISTINCT ingredient_id FROM recipe_ingredient);
        """
        db.session.execute(text(sql_query))
        db.session.commit()
        return {"message": "All ingredients without relations successfully deleted"}
    except IntegrityError:
        # Handle IntegrityError
        return {"error": "An integrity error occurred"}


@ingredient_bp.route("/delete/<int:ing_id>", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_ingredient_by_id(ing_id):
    if ing_id:
        existing_recipe = (
            db.session.query(RecipeIngredient).filter_by(ingredient_id=ing_id).first()
        )
        if existing_recipe is None:
            ingredient = db.session.query(Ingredient).get(
                ing_id
            )  # Use .get() to retrieve the ingredient by ID
            if ingredient:
                db.session.delete(ingredient)
                db.session.commit()
                return {"message": f"Ingredient with id {ing_id} successfully deleted"}
            else:
                return {"error": f"Ingredient with id {ing_id} not found"}
        else:
            return {
                "error": f"Couldn't delete ingredient with ID {ing_id} as it has relations with 1 or more recipes"
            }
