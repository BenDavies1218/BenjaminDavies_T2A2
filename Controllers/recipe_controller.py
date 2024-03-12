from sqlalchemy import func
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from Models.recipe import Recipe, recipe_schema, recipes_schema
from Models.ingredient import Ingredient
from Models.allergy import Allergy
from Models.recipe_allergies import RecipeAllergy
from Models.recipe_ingredients import RecipeIngredient
from Models.user import User

db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE

"""
POST data sample
{
    "title": "Spaghetti Carbonara",
    "difficulty": 3,
    "serving_size": 4,
    "instructions": "1. Cook pasta according to package instructions. 2. In a large skillet, cook bacon until crispy. 3. Drain pasta and add it to the skillet with bacon. 4. In a separate bowl, mix eggs and cheese. 5. Pour egg mixture over pasta and bacon, stirring quickly to coat. 6. Serve hot and enjoy!",
    "ingredients": {
        "pasta": "500g",
        "bacon": "200g",
        "eggs": "4",
        "Parmesan cheese": "100g",
        "salt": "to taste",
        "black pepper": "to taste"
    },
    "allergies": ["gluten", "lactose", "egg"]
}
"""


# Create a new recipe in the database
@db_recipes.route("/create", methods=["POST"])
@jwt_required()
def create_recipe():
    # need to add jwt for user id
    body_data = request.get_json()

    if Recipe.query.filter_by(title=body_data.get("title")).first():
        return {"error": "recipe already exists"}

    user_id = get_jwt_identity()

    # Query the user from the database using the user ID
    user = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return {"error": "User not found"}, 404

    # create recipe object
    recipe = Recipe(
        title=body_data.get("title"),
        user=user,
        difficulty=body_data.get("difficulty"),
        serving_size=body_data.get("serving_size"),
        instructions=body_data.get("instructions"),
    )

    recipe = Recipe.query.filter_by(title=body_data.get("title")).first()

    # add ingredients to recipe
    ingredients_data = body_data.get("ingredients")
    if ingredients_data:
        for ingredient_name, amount in ingredients_data.items():
            ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
            if not ingredient:
                # Ingredient doesn't exist create it
                ingredient = Ingredient(name=ingredient_name)
                db.session.add(ingredient)

            # Create RecipeIngredient relation
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id, ingredient_id=ingredient.id, amount=amount
            )
            db.session.add(recipe_ingredient)
    db.session.commit()

    # add allergy to recipe
    allergies = body_data.get("allergies")
    if allergies:
        for allergy_name in allergies:
            allergy = Allergy.query.filter_by(name=allergy_name).first()
            if not allergy:
                # Allergy doesn't exist, create it
                allergy = Allergy(name=allergy_name)
                db.session.add(allergy)
        db.session.commit()

    # Create RecipeAllergy relation inside the loop
    recipe_allergy = RecipeAllergy(recipe_id=recipe.id, allergy_id=allergy.id)
    db.session.add(recipe_allergy)

    # Commit changes after the loop
    db.session.commit()
    return {"message": "Recipe created successfully"}, 201


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


# Get Data on all recipes in the database
@db_recipes.route("/")
@jwt_required()
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
    item = request.args.get("s")
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
