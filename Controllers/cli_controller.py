import random
from datetime import date
from seeding_function import seed
from flask import Blueprint
from init import db, bcrypt
from Models.user import User
from Models.review import Review
from Models.allergy import Allergy
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
    # Create users
    user1 = User(
        name="John Doe",
        email="john@example.com",
        password="password",
        is_admin=False,
        created=date.today(),
    )
    user2 = User(
        name="Jane Smith",
        email="jane@example.com",
        password="password",
        is_admin=False,
        created=date.today(),
    )

    # Add users to session
    db.session.add(user1)
    db.session.add(user2)

    # Create ingredients
    ingredient1 = Ingredient(name="Pasta")
    ingredient2 = Ingredient(name="Eggs")
    ingredient3 = Ingredient(name="Bacon")
    ingredient4 = Ingredient(name="Parmesan Cheese")

    # Add ingredients to session
    db.session.add(ingredient1)
    db.session.add(ingredient2)
    db.session.add(ingredient3)
    db.session.add(ingredient4)

    # Create allergies
    allergy1 = Allergy(name="Gluten")
    allergy2 = Allergy(name="Lactose")

    # Add allergies to session
    db.session.add(allergy1)
    db.session.add(allergy2)

    # Create recipes
    recipe1 = Recipe(
        title="Spaghetti Carbonara",
        user=user1,
        difficulty=3,
        serving_size=4,
        instructions="Cook spaghetti, mix with eggs, cheese, and bacon.",
        created=date.today(),
    )

    recipe2 = Recipe(
        title="Scrambled Eggs",
        user=user2,
        difficulty=1,
        serving_size=2,
        instructions="Scramble eggs in a pan until cooked.",
        created=date.today(),
    )

    # Add recipes to session
    db.session.add(recipe1)
    db.session.add(recipe2)

    # Create reviews
    review1 = Review(
        details="Delicious recipe!",
        rating=5,
        created=date.today(),
        user=user1,
        recipe=recipe1,
    )
    review2 = Review(
        details="Simple and tasty!",
        rating=4,
        created=date.today(),
        user=user2,
        recipe=recipe2,
    )

    # Add reviews to session
    db.session.add(review1)
    db.session.add(review2)

    # Create recipe-ingredient associations
    recipe_ingredient1 = RecipeIngredient(
        recipe=recipe1, ingredient=ingredient1, amount="200g"
    )
    recipe_ingredient2 = RecipeIngredient(
        recipe=recipe1, ingredient=ingredient2, amount="3"
    )
    recipe_ingredient3 = RecipeIngredient(
        recipe=recipe1, ingredient=ingredient3, amount="100g"
    )
    recipe_ingredient4 = RecipeIngredient(
        recipe=recipe1, ingredient=ingredient4, amount="50g"
    )

    recipe_ingredient5 = RecipeIngredient(
        recipe=recipe2, ingredient=ingredient2, amount="4"
    )

    # Add recipe-ingredient associations to session
    db.session.add(recipe_ingredient1)
    db.session.add(recipe_ingredient2)
    db.session.add(recipe_ingredient3)
    db.session.add(recipe_ingredient4)
    db.session.add(recipe_ingredient5)

    # Create recipe-allergy associations
    recipe_allergy1 = RecipeAllergy(recipe=recipe1, allergy=allergy1)
    recipe_allergy2 = RecipeAllergy(recipe=recipe1, allergy=allergy2)

    # Add recipe-allergy associations to session
    db.session.add(recipe_allergy1)
    db.session.add(recipe_allergy2)

    # Commit the session to persist the changes to the database
    db.session.commit()

    print("Tables seeded")
