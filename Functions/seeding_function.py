from Models.user import User
from Models.review import Review
from Models.recipe import Recipe
from Models.ingredient import Ingredient
from init import bcrypt
from datetime import date
import random


def seed():
    users_data = [
        User(
            email="admin@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin=True,
        ),
        User(
            name="Benjamin Davies",
            email="user1@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
        ),
    ]
    review_data = []
    REVIEW_STRING = ["Great", "eggsalent"]
    for i in range(10):
        dt = REVIEW_STRING[i]
        RATING = random.randint(3, 10)
        review_data.append(
            Review(
                details="this is a great recipe",
                rating=RATING,
                created=date.today(),
                user=users_data[1],
            )
        )
        dt = REVIEW_STRING[i + 1]

    recipe_data = [
        Ingredient(name="fish"),
        Recipe(
            Title="beef chicken noodle",
            user_id=users_data[1],
            review_id=review_data[1],
            ingredient_id=[0],
            difficulty=5,
            serving_size=2,
            instructions="cook all together",
            allergy_id=["beef", "gluten"],
        ),
    ]
    return users_data, review_data
