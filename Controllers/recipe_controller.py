from sqlalchemy import func
from flask import Blueprint, request
from init import db
from Models.recipe import Recipe, recipe_schema, recipes_schema
from Models.review import Review, review_schema, reviews_schema
from Models.user import User, user_schema, users_schema
from Models.ingredient import Ingredient, recipe_ingredient_schema
from Models.recipe_ingredients import RecipeIngredient

db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


# ------------------------------------------------------------------
# CRUD - CREATE


# Create a new Recipe in the database
@db_recipes.route("/Create")
def create_recipe():
    body_data = request.get_json()


# -------------------------------------------------------------------
# CRUD - READ


# Get Data on all recipes in the database
@db_recipes.route("/")
def get_all_recipes():
    stmt = db.select(Recipe)
    recipes = db.session.scalars(stmt)
    return recipes_schema.dump(recipes)


# Get data on one recipe in the database
@db_recipes.route("/<int:recipe_id>")
def get_recipe(recipe_id):
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    recipe = db.session.scalar(stmt)
    return recipe_schema.dump(recipe)


# search for a recipe with specific ingredient in the database
@db_recipes.route("/search")
def get_recipe_by_ingredient():
    item = "past".lower()
    recipes = (
        db.session.query(Recipe)
        .join(RecipeIngredient)
        .join(Ingredient)
        .filter(func.lower(Ingredient.name) == item)
        .all()
    )

    # Manually create a list of dictionaries representing each recipe
    if len(recipes) > 0:
        serialized_recipes = []
        for recipe in recipes:
            serialized_recipe = {
                "id": recipe.id,
                "title": recipe.title,
                "difficulty": recipe.difficulty,
                "serving_size": recipe.serving_size,
                "instructions": recipe.instructions,
                "ingredients": recipe.ingredients,
                "user": recipe.user,
                "allergies": recipe.allergies,
                "reviews": recipe.reviews,
            }
            serialized_recipes.append(serialized_recipe)

        # Serialize the list of dictionaries to JSON
        return recipe_schema.dump(serialized_recipe)
    else:
        return {"Error": f"No recipes found with the ingredient '{item}'. "}
