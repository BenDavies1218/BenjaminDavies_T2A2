from Models.user import User
from Models.review import Review
from init import bcrypt
from datetime import date
import random

REVIEW_STRING = ["Great", "eggsalent"]


def seed(REVIEW_STRING):
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
    return users_data, review_data
