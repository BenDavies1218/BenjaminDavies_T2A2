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
from Functions.Decorator_functions import user_owner, any_user

db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


# Create a new recipe in the database
@db_recipes.route("/create", methods=["POST"])
@jwt_required()
@any_user
def create_recipe():
    try:
        body_data = recipe_schema.load(request.get_json())

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
            for allergy_data in allergies:
                # query to see if the allergy exists already
                allergy_name = allergy_data.get("allergy", {}).get("name")
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
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Recipe title already in use"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


# Get Data on all recipes in the database
@db_recipes.route("/")
@jwt_required()
@any_user
def get_all_recipes():
    # select all recipes
    stmt = db.select(Recipe)
    # serialized it
    recipes = db.session.scalars(stmt)
    # return to user
    return recipes_schema.dump(recipes), 200


# Get data on one recipe in the database pass the recipe id as an argument
@db_recipes.route("/<int:recipe_id>")
@jwt_required()
@any_user
def get_recipe(recipe_id):
    # select recipe by the id
    stmt = db.select(Recipe).filter_by(id=recipe_id)
    # serialize it
    recipe = db.session.scalar(stmt)
    # return to the user
    return recipe_schema.dump(recipe), 200


# search for a recipe with specific ingredient or title in the database requires query parameter
# acceptable parameters names ["ingredient", "title"]
@db_recipes.route("/search")
@jwt_required()
@any_user
def get_recipe_by_ingredient():
    # route handles 2 possible query parameters
    ingredient = request.args.get("ingredient")
    title = request.args.get("title")

    # if no query is sent it will return a error message with code 400 for bad request
    if not ingredient and not title:
        return {"Error": "Please provide either 'ingredient' or 'title'."}, 400

    # first check if the ingredient parameter is true
    if ingredient:
        # Construct the SQL query to search for the recipes with that ingredient. I tried to use sql alchmey but I couldn't query the data properly, but the raw sql works fine.
        """
        # Main query
        SELECT * FROM recipes     =      selects all columns from recipes in the database

        #sub query 1
        WHERE id IN (SELECT recipe_id FROM recipe_ingredient)      =      selects the ingredients that are in specific recipe

        # sub query 2
        WHERE ingredient_id IN (SELECT id FROM ingredient WHERE LOWER(name) LIKE LOWER (:ingredient))     =      selects the ingredients that is like the ingredient variable that is passed to query, I used lower so it becomes a case insensitive search.
        """

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

        # Execute the SQL query with the provided ingredient variable
        recipes = db.session.execute(
            text(sql_query), {"ingredient": f"%{ingredient}%"}
        ).fetchall()

        # Check if any recipes were found
        if recipes:
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
# i first tried to check if each ingredient existed but gave up trying to make it work and decide to delete each ingredient and allergy. then create a new instance from the data that is passed through the request.


# pass the recipe id as an argument
@db_recipes.route("/<int:recipe_id>", methods=["PUT", "PATCH"])
@jwt_required()
@user_owner
def update_recipe(recipe_id):
    try:
        # retrieve the json body
        body_data = recipe_schema.load(request.get_json(), partial=True)

        # select the recipe by id
        stmt = db.select(Recipe).filter_by(id=recipe_id)
        recipe = db.session.scalar(stmt)

        # check that the recipe with specific id exists
        if recipe:
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
                    ingredient = Ingredient.query.filter_by(
                        name=ingredient_name
                    ).first()
                    # if it doesn't we create a new instance of the ingredient
                    if not ingredient:
                        ingredient = Ingredient(name=ingredient_name)
                        db.session.add(ingredient)
                        db.session.commit()

                    # Create RecipeIngredient instance this will not exist as we are creating this recipe_ingredient relation for the first time
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id, ingredient=ingredient, amount=amount
                    )

                    db.session.add(recipe_ingredient)
                    db.session.commit()

            # same implementation as above delete all the current recipeallergy relations then create a new instance for each
            allergy_data = body_data.get("allergies")

            db.session.query(RecipeAllergy).filter_by(recipe_id=recipe_id).delete()

            if allergy_data:
                # create a loop to add each new instance
                for allergy in allergy_data:
                    # first check if the allergy exists
                    exists = db.session.query(Allergy).filter_by(name=allergy).first()
                    # if it doesn't exist we create a new instance
                    new = Allergy(name=allergy)

                    if not exists:
                        db.session.add(new)
                        db.session.commit()

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

    except DataError as err:
        return {"error": str(err)}, 400

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Recipe title already in use"}, 409


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
        # quering the recipeingredients by recipe id and delete each instance
        db.session.query(RecipeIngredient).filter_by(recipe_id=recipe_id).delete()

        # query Recipeallergy by recipe id and delete each instance
        db.session.query(RecipeAllergy).filter_by(recipe_id=recipe_id).delete()

        # query reviews and delete by recipe id
        db.session.query(Review).filter_by(recipe_id=recipe_id).delete()

        # now delete the recipe and commit to the database
        db.session.delete(recipe)
        db.session.commit()

        # return simple message to the user with 204 code for successfully deletion
        return {"message": f"recipe with id {recipe_id} was successfully deleted"}, 204

    # we cant find the recipe with that id so return a not found status code
    else:
        return {"error": f"Recipe with id {recipe_id} not found"}, 404
