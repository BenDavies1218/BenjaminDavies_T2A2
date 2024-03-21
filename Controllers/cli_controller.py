from datetime import date
from flask import Blueprint
from init import db
from Functions.seeding_function import seed_data

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
    # using a separete module in my functions folder to create the seeding data, just cleans up my cli.controller a bit.
    (
        user,
        recipes,
        ingredients,
        allergies,
        recipe_ingredients,
        recipe_allergies,
        reviews,
    ) = seed_data()

    # Create the users first as recipes require a user id to be created
    db.session.add_all(user)
    db.session.commit()

    # add data to recipes, ingredients, allergies tables
    db.session.add_all(recipes)
    db.session.add_all(ingredients)
    db.session.add_all(allergies)
    db.session.commit()

    # add recipe ingredient and recipe allergy relations
    db.session.add_all(recipe_ingredients)
    db.session.add_all(recipe_allergies)

    # add reviews to the recipes
    db.session.add_all(reviews)

    db.session.commit()
    print("Tables seeded")
