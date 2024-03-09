from flask import Blueprint
from init import db
from Models.recipe import Recipe, recipe_schema, recipes_schema
from Models.review import Review, review_schema, reviews_schema
from Models.user import User, user_schema, users_schema


db_recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


@db_recipes.route("/")
def get_all_recipes():
    stmt = db.select(Recipe)
    recipes = db.session.scalars(stmt)
    return recipes_schema.dump(recipes)
