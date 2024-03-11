from sqlalchemy import func
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from Models.recipe import Recipe, recipe_schema, recipes_schema
from Models.ingredient import Ingredient
from Models.allergy import Allergy
from Models.recipe_allergies import RecipeAllergy
from Models.recipe_ingredients import RecipeIngredient

db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE

"""
POST data
{
    "title": "string",
    "difficulty": int,
    "serving_size": int,
    "instructions": "text",
    "ingredients": {"pasta": "500g", "bacon": "200g"},
    "allergies": ["string", "nullable=True"],
}
"""


# Create a new recipe in the database
@db_recipes.route("/create", methods=["POST"])
def create_recipe():
    # need to add jwt for user id
    body_data = request.get_json()

    # create recipe object
    recipe = Recipe(
        title=body_data.get("title"),
        user=body_data.get("user"),
        difficulty=body_data.get("difficulty"),
        serving_size=body_data.get("serving_size"),
        instructions=body_data.get("instructions"),
    )
    db.session.add(recipe)
    db.session.commit()

    # add ingredients to recipe
    ingredients_data = body_data.get("ingredients")
    for ingredient_name, amount in ingredients_data.items():
        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if not ingredient:
            # Ingredient doesn't exist create it
            ingredient = Ingredient(name=ingredient_name)
            db.session.add(ingredient)

        # Create RecipeIngredient relation
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=amount
        )
        db.session.add(recipe_ingredient)
    db.session.commit()

    # add allergy to recipe
    allergies = body_data.get("allergies")
    if allergies:
        for allergy_name in allergies:
            allergy = Allergy.query.filter_by(name=allergy_name).first()
            if not allergy:
                # Allergy doesn't exist create it
                allergy = Allergy(name=allergy_name)
                db.session.add(allergy)

            # Create RecipeAllergy relation
            recipe_allergies = RecipeAllergy(recipe_id=recipe.id, allergy_id=allergy.id)
            db.session.add(recipe_allergies)
        db.session.commit()
    return {"message": "Recipe created successfully"}, 201


# -------------------------------------------------------------------
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
    if recipes:
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
        return {"Error": f"No recipes found with the ingredient '{item}'. "}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE
