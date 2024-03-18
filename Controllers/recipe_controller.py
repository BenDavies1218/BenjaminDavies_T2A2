from sqlalchemy import func, text
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from sqlalchemy.exc import IntegrityError, DataError
from Models.recipe import Recipe, recipe_schema, recipes_schema
from Models.ingredient import Ingredient
from Models.allergy import Allergy
from Models.recipe_allergies import RecipeAllergy
from Models.recipe_ingredients import RecipeIngredient
from Models.user import User
from Models.review import Review
from psycopg2 import errorcodes
from Functions.Decorator_functions import user_owner

db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE

"""
POST data sample
{
    "title": "meatballs",
    "difficulty": 5,
    "serving_size": 4,
    "instructions": "1. Start by chopping all ingredients 2. mix together with herbs and spices 3. roll into round 3cm balls 4. bake in oven for 20 minutes until cooked 5. make tomato sauce 6. combine everything and eat.",
    "ingredients": {
        "beef": "500g",
        "onion": "2 whole",
        "eggs": "2",
        "Parmesan cheese": "100g",
        "breadcrumbs": "100gm",
        "herbs": "2 Tablespoon",
        "tomato sauce": "500ml",
        "salt": "to taste",
        "black pepper": "to taste"
    },
    "allergies": ["gluten", "dairy"]
}
"""


# Create a new recipe in the database
@db_recipes.route("/create", methods=["POST"])
@jwt_required()
def create_recipe():
    try:
        body_data = recipe_schema.load(request.get_json())

        fields = {
            "title": str,
            "difficulty": int,
            "serving_size": int,
            "instructions": str,
            "ingredients": list,
        }

        for field, data_type in fields.items():
            if field not in body_data:
                return {"error": f"Field '{field}' is required"}, 400
            if not isinstance(body_data[field], data_type):
                return {
                    "error": f"Field '{field}' must be of type '{data_type.__name__}'"
                }, 400

        # check if recipe title already exists as I wanted the recipe title to be unique in this API even though the ERD model and relations would allow for duplicate recipes title.
        if Recipe.query.filter_by(title=body_data.get("title")).first():
            return {"error": "Recipe title already in use"}, 409
        # get the user identity
        user_id = get_jwt_identity()
        # get the user's name and email
        user = User.query.get(user_id)

        # Check if the user exists
        if not user:
            return {"error": "User not found"}, 404

        # create recipe instance
        recipe = Recipe(
            title=body_data.get("title"),
            user=user,
            difficulty=body_data.get("difficulty"),
            serving_size=body_data.get("serving_size"),
            instructions=body_data.get("instructions"),
        )
        # add and commit to database before making related tables
        db.session.add(recipe)
        db.session.commit()

        # get id of new recipe
        recipe = Recipe.query.filter_by(title=recipe.title).first()

        # add ingredients to recipe
        ingredients_data = body_data.get("ingredients")
        if ingredients_data:
            # I decided that I would send this data into the api as a list of dictonaries { ingredient: {"name": "ingredient"}, "amount": "String" },  this made the most logical sense to pass the ingredient with the amount.
            for ingredient_data in ingredients_data:
                ingredient_name = ingredient_data.get("ingredient", {}).get("name")
                amount = ingredient_data.get("amount")
                # check if ingredient exist in database
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                # if it doesn't we create a new instance of the ingredient
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    db.session.add(ingredient)
                    db.session.commit()

                # Create RecipeIngredient instance this will not exist as we are creating this recipe for the first time
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id, ingredient=ingredient, amount=amount
                )

                db.session.add(recipe_ingredient)
                db.session.commit()

        # add allergies to recipe
        allergies = body_data.get("allergies")
        if allergies:
            # I decide allgeries could just be a simple list when sent to the api
            for allergy_name in allergies:
                # query to see if the allergy exists already
                allergy = Allergy.query.filter_by(name=allergy_name).first()
                # if it doesn't we create a new instance
                if not allergy:
                    allergy = Allergy(name=allergy_name)
                    db.session.add(allergy)
                    db.session.commit()

                # Create RecipeAllergy relation this will also be unique as we creating this for the first time
                recipe_allergy = RecipeAllergy(
                    recipe_id=recipe.id, allergy_id=allergy.id
                )
                db.session.add(recipe_allergy)
                db.session.commit()

        # simple return msg with recipe title and 201 created code
        return {"message": f"Recipe {recipe.title} was created successfully"}, 201

    except DataError as err:
        return {"error": str(err)}, 400

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Recipe title already in use"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


# Get Data on all recipes in the database
@db_recipes.route("/")
@jwt_required()
def get_all_recipes():
    # select all recipes
    stmt = db.select(Recipe)
    # serialized it
    recipes = db.session.scalars(stmt)
    # return to user
    return recipes_schema.dump(recipes), 200


# Get data on one recipe in the database pass the recipe id as an argument
@db_recipes.route("/<int:recipe_id>")
def get_recipe(recipe_id):
    # select recipe by the id
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    # serialize it
    recipe = db.session.scalar(stmt)
    # return to the user
    return recipe_schema.dump(recipe), 200


# search for a recipe with specific ingredient or title in the database requires query parameter
# acceptable parameters ["ingredient", "title"]
@db_recipes.route("/search")
def get_recipe_by_ingredient():
    # route handles 2 possible query parameters
    ingredient = request.args.get("ingredient")
    title = request.args.get("title")

    # if no query is sent it will return a error message with code 400 for bad request
    if not ingredient and not title:
        return {"Error": "Please provide either 'ingredient' or 'title'."}, 400

    # first check if the ingredient parameter is true
    if ingredient:
        # Construct the SQL query to search for the recipes with that ingredient. I tried to use sql alchmey but for some reason it had problems dumping the data properly, but the raw sql works.
        sql_query = """
            SELECT *
            FROM recipes
            WHERE id IN (
            SELECT recipe_id
            FROM recipe_ingredient
            WHERE ingredient_id IN (
                SELECT id
                FROM ingredient
                WHERE LOWER(name) LIKE LOWER(:ingredient)
            )
        );
        """

        # Execute the SQL query with the provided ingredient parameter
        recipes = db.session.execute(
            text(sql_query), {"ingredient": f"%{ingredient}%"}
        ).fetchall()

        # Check if any recipes were found
        if recipes:
            print(recipes)
            return recipes_schema.dump(recipes), 200

        else:
            return {
                "Error": f"No recipes with the ingredient '{ingredient}' found."
            }, 404

    # check if the title query is true
    if title:
        # just query the recipe for its name using the ilike function again
        recipes_by_name = (
            db.session.query(Recipe)
            .filter(func.lower(Recipe.title).ilike(f"%{title.lower()}%"))
            .all()
        )
        #  if it finds a recipe that is similar return it will return it
        if recipes_by_name:
            return recipes_schema.dump(recipes_by_name), 200
        # simple error msg if it cant find a similar recipe
        else:
            return {"Error": f"No recipes with the title '{title}' found."}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


# pass the recipe id as an argument
@db_recipes.route("/<int:recipe_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_recipe(recipe_id):
    # check if the user is an admin
    user_id = get_jwt_identity()
    is_admin = db.session.query(User.is_admin).filter_by(id=user_id).scalar()

    # retrieve the json body
    body_data = recipe_schema.load(request.get_json(), partial=True)
    # select the recipe by id
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    recipe = db.session.scalar(stmt)

    # check that the recipe with specific id exists
    if recipe:
        # checks that the user is authorized to edit the recipe or if the user is an admin
        if str(recipe.user_id) != str(user_id) and not is_admin:
            return {
                "error": "Only the recipe owner or an administrator can edit the recipe"
            }, 401

        # Update recipe fields that have no relations
        recipe.title = body_data.get("title") or recipe.title
        recipe.difficulty = body_data.get("difficulty") or recipe.difficulty
        recipe.serving_size = body_data.get("serving_size") or recipe.serving_size
        recipe.instructions = body_data.get("instructions") or recipe.instructions

        # get the json data for ingredients which in our case is a list of dictonaries
        ingredients_data = body_data.get("ingredients")
        # delete the current recipeIngredients for the recipe
        db.session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).delete()

        # Check if ingredients exist and add them if not
        if ingredients_data:
            for ingredient_data in ingredients_data:
                ingredient_name = ingredient_data.get("ingredient", {}).get("name")
                amount = ingredient_data.get("amount")
                # check if ingredient exist in database
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                # if it doesn't we create a new instance of the ingredient
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    db.session.add(ingredient)
                    db.session.commit()

                # Create RecipeIngredient instance this will not exist as we are creating this recipe for the first time
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id, ingredient=ingredient, amount=amount
                )

                db.session.add(recipe_ingredient)
                db.session.commit()

        # same implementation as above delete all the current recipeallergy relations then create a new instance for each
        allergy_data = body_data.get("allergies")
        db.session.query(RecipeAllergy).filter_by(recipe_id=recipe_id).delete()
        if allergy_data:
            # only differce is this data is a list not a dictonary
            for allergy in allergy_data:
                exists = db.session.query(Allergy).filter_by(name=allergy).first()
                new = Allergy(name=allergy)
                if not exists:
                    db.session.add(new)
                    db.session.commit()
                # again getting the value for exists as if the allergy didn't exist before we commited on the previous line then the id wouldn't exist so we need to do this
                exists = db.session.query(Allergy).filter_by(name=allergy).first()
                # creating the new recipeallergy instance
                recipe_allergy = RecipeAllergy(
                    recipe_id=recipe_id, allergy_id=exists.id
                )
                db.session.add(recipe_allergy)
                db.session.commit()
        # recipe the updated recipe to the user with code 200
        return {"message": f"Recipe {recipe_id} was successfully updated"}, 200
    else:
        return {"error": f"Recipe with id '{recipe_id}' not found"}, 404


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


# pass the recipe id as an argument
@db_recipes.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
@user_owner
def delete_recipe(recipe_id):
    # query for the recipe that we want to delete
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    recipe = db.session.scalar(stmt)

    # check if recipe exists
    if recipe:
        db.session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).delete()
        db.session.query(RecipeAllergy).where(
            RecipeAllergy.recipe_id == recipe_id
        ).delete()
        db.session.query(Review).filter_by(recipe_id=recipe_id).delete()
        # now delete the recipe and commit to the database
        db.session.delete(recipe)
        db.session.commit()
        # return simple message to the user with 204 code for successfully deletion
        return {"message": f"recipe with id {recipe_id} was successfully deleted"}, 200

    # we cant find the recipe with that id so return a not found status code
    else:
        return {"error": f"Recipe with id {recipe_id} not found"}, 404
