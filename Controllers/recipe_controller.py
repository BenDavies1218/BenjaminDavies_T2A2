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
    "allergies": ["gluten", "lactose", "eggs"]
}
"""


# Create a new recipe in the database
@db_recipes.route("/create", methods=["POST"])
@jwt_required()
def create_recipe():
    body_data = request.get_json()
    recipe_name = body_data.get("title")

    if Recipe.query.filter_by(title=recipe_name).first():
        return {"message": f"Recipe for {recipe_name} already exists"}

    user_id = get_jwt_identity()
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
    db.session.add(recipe)
    db.session.commit()

    # Retrieve the newly created recipe to get its ID
    recipe = Recipe.query.filter_by(title=recipe_name).first()

    # Add ingredients to recipe
    ingredients_data = body_data.get("ingredients")
    if ingredients_data:
        for ingredient_name, amount in ingredients_data.items():
            ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name)
                db.session.add(ingredient)
                db.session.commit()

            # Create RecipeIngredient table
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id, ingredient_id=ingredient.id, amount=amount
            )
            db.session.add(recipe_ingredient)
            db.session.commit()

    # Add allergies to recipe
    allergies = body_data.get("allergies")
    if allergies:
        for allergy_name in allergies:
            allergy = Allergy.query.filter_by(name=allergy_name).first()
            if not allergy:
                allergy = Allergy(name=allergy_name)
                db.session.add(allergy)
                db.session.commit()

            # Create RecipeAllergy table
            recipe_allergy = RecipeAllergy(recipe_id=recipe.id, allergy_id=allergy.id)
            db.session.add(recipe_allergy)
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


# search for a recipe with specific ingredient in the database requires query parameter
@db_recipes.route("/search")
def get_recipe_by_ingredient():
    ingredient = request.args.get("ingredient")
    title = request.args.get("title")
    recipes_ingredient = (
        db.session.query(Recipe)
        .join(RecipeIngredient)
        .join(Ingredient)
        .filter(func.lower(Ingredient.name) == ingredient.lower())
        .all()
    )
    if recipes_ingredient:
        return recipes_schema.dump(recipes_ingredient)
    else:
        return {"Error": f"No recipes with the ingredient '{ingredient}' found. "}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


@db_recipes.route("/<int:recipe_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_recipe(recipe_id):
    user_id = get_jwt_identity()
    is_admin = db.session.query(User.is_admin).filter_by(id=user_id).scalar()

    body_data = recipe_schema.load(request.get_json(), partial=True)
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    recipe = db.session.scalar(stmt)

    if recipe:
        if str(recipe.user_id) != str(user_id) and not is_admin:
            return {
                "error": "Only the recipe owner or an administrator can edit the recipe"
            }

        # Update recipe fields
        recipe.title = body_data.get("title") or recipe.title
        recipe.difficulty = body_data.get("difficulty") or recipe.difficulty
        recipe.serving_size = body_data.get("serving_size") or recipe.serving_size
        recipe.instructions = body_data.get("instructions") or recipe.instructions

        # Check if ingredients exist and add them if not
        ingredients_data = body_data.get("ingredients")
        if ingredients_data:
            for ingredient_data in ingredients_data:
                ingredient = (
                    db.session.query(Ingredient)
                    .filter_by(name=ingredient_data["name"])
                    .first()
                )
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_data["name"])
                    db.session.add(ingredient)
                    db.session.commit()

                # Update or create RecipeIngredient table
                recipe_ingredient = RecipeIngredient.query.filter_by(
                    recipe_id=recipe_id, ingredient_id=ingredient.id
                ).first()

                if recipe_ingredient:
                    recipe_ingredient.amount = ingredient_data.get("amount")
                else:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe_id,
                        ingredient_id=ingredient.id,
                        amount=ingredient_data.get("amount"),
                    )
                    db.session.add(recipe_ingredient)

            db.session.commit()

        return recipe_schema.dump(recipe)
    else:
        return {"error": "Recipe not found"}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE
