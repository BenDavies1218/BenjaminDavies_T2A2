import random
from datetime import date
from Functions.seeding_function import seed
from flask import Blueprint
from init import db, bcrypt
from Models.user import User
from Models.review import Review
from Models.ingredient import Ingredient
from Models.recipe import Recipe
from Models.recipe_allergies import RecipeAllergy
from Models.recipe_ingredients import RecipeIngredient

db_commands = Blueprint("db", __name__)


@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")


@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")


@db_commands.cli.command("seed")
def seed_tables():
    # Users
    users_data = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password",
            "is_admin": False,
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password": "password",
            "is_admin": False,
        },
    ]
    users = [User(created=date.today(), **data) for data in users_data]
    db.session.add_all(users)

    # Ingredients
    ingredients_data = ["Pasta", "Eggs", "Bacon", "Parmesan Cheese"]
    ingredients = [Ingredient(name=name) for name in ingredients_data]
    db.session.add_all(ingredients)

    # Allergies
    allergies_data = ["Gluten", "Lactose"]
    allergies = [Allergy(name=name) for name in allergies_data]
    db.session.add_all(allergies)

    # Recipes
    recipes_data = [
        {
            "title": "Spaghetti Carbonara",
            "user": users[0],
            "difficulty": 3,
            "serving_size": 4,
            "instructions": "Cook spaghetti, mix with eggs, cheese, and bacon.",
        },
        {
            "title": "Scrambled Eggs",
            "user": users[1],
            "difficulty": 1,
            "serving_size": 2,
            "instructions": "Scramble eggs in a pan until cooked.",
        },
    ]
    # Loop to add date for each entry
    recipes = [Recipe(created=date.today(), **data) for data in recipes_data]
    db.session.add_all(recipes)

    # Reviews
    reviews_data = [
        {
            "details": "Delicious recipe!",
            "rating": 5,
            "user": users[0],
            "recipe": recipes[0],
        },
        {
            "details": "Simple and tasty!",
            "rating": 4,
            "user": users[1],
            "recipe": recipes[1],
        },
    ]
    reviews = [Review(created=date.today(), **data) for data in reviews_data]
    db.session.add_all(reviews)

    # Recipe-Ingredient
    recipe_ingredient_data = [
        {"recipe": recipes[0], "ingredient": ingredients[0], "amount": "200g"},
        {"recipe": recipes[0], "ingredient": ingredients[1], "amount": "3"},
        {"recipe": recipes[0], "ingredient": ingredients[2], "amount": "100g"},
        {"recipe": recipes[0], "ingredient": ingredients[3], "amount": "50g"},
        {"recipe": recipes[1], "ingredient": ingredients[1], "amount": "4"},
    ]
    recipe_ingredients = [RecipeIngredient(**data) for data in recipe_ingredient_data]
    db.session.add_all(recipe_ingredients)

    # Recipe-Allergy
    recipe_allergy_data = [
        {"recipe": recipes[0], "allergy": allergies[0]},
        {"recipe": recipes[0], "allergy": allergies[1]},
    ]
    recipe_allergies = [RecipeAllergy(**data) for data in recipe_allergy_data]
    db.session.add_all(recipe_allergies)

    # Commit the session
    db.session.commit()

    print("Tables seeded")
