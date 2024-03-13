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
from Models.review import Review

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

    # get id of recipe
    recipe = Recipe.query.filter_by(title=recipe_name).first()

    # add ingredients to recipe
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

    if not ingredient and not title:
        return {"Error": "Please provide either 'ingredient' or 'title'."}, 400

    if ingredient:
        recipes_ingredient = (
            db.session.query(Recipe)
            .join(RecipeIngredient)
            .join(Ingredient)
            .filter(func.lower(Ingredient.name).ilike(f"%{ingredient.lower()}%"))
            .all()
        )
        if recipes_ingredient:
            return recipes_schema.dump(recipes_ingredient)
        else:
            return {
                "Error": f"No recipes with the ingredient '{ingredient}' found."
            }, 404

    if title:
        recipes_by_name = (
            db.session.query(Recipe)
            .filter(func.lower(Recipe.title).ilike(f"%{title.lower()}%"))
            .all()
        )
        if recipes_by_name:
            return recipes_schema.dump(recipes_by_name)
        else:
            return {"Error": f"No recipes with the title '{title}' found."}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


@db_recipes.route("/<int:recipe_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_recipe(recipe_id):
    user_id = get_jwt_identity()
    is_admin = db.session.query(User.is_admin).filter_by(id=user_id).scalar()

    body_data = request.get_json()
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
            for ingredient, amount in ingredients_data.items():
                ingredient = (
                    db.session.query(Ingredient).filter_by(name=ingredient).first()
                )
                if not ingredient:
                    new_ingredient = Ingredient(name=ingredient)
                    db.session.add(new_ingredient)
                    db.session.commit()

                # Update or create RecipeIngredient table
                recipe_ingredient = (
                    db.session.query(RecipeIngredient)
                    .filter_by(recipe_id=recipe_id, ingredient_id=ingredient.id)
                    .first()
                )

                if recipe_ingredient:
                    recipe_ingredient.amount = amount
                else:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe_id, ingredient_id=ingredient.id, amount=amount
                    )
                    db.session.add(recipe_ingredient)

            db.session.commit()

        return recipe_schema.dump(recipe)
    else:
        return {"error": "Recipe not found"}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@db_recipes.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    user_id = get_jwt_identity()
    is_admin = db.session.query(User.is_admin).filter_by(id=user_id).scalar()

    stmt = db.select(Recipe).filter_by(id=recipe_id)
    recipe = db.session.scalar(stmt)

    # Delete related tables first to avoid foriegn key null errors
    db.session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).delete()
    db.session.query(RecipeAllergy).where(RecipeAllergy.recipe_id == recipe_id).delete()
    db.session.query(Review).filter_by(recipe_id=recipe_id).delete()

    # check if recipe exists
    if recipe:
        # check if recipe is owned by user
        if str(recipe.user_id) != str(user_id) and not is_admin:
            return {
                "error": "Only the recipe owner or an administrator can delete the recipe"
            }
        db.session.delete(recipe)
        db.session.commit()
        return {"message": f"recipe with id {recipe_id} was successfully deleted"}, 204
    else:
        return {"error": f"Recipe with id {recipe_id} not found"}, 404
