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
            email="Simon@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin=True,
        ),
        User(
            name="Benjamin Davies",
            email="user1@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
        ),
        User(
            email="luis@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
        ),
        User(
            name="dan@email.com",
            email="user1@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
        ),
        User(
            email="jairo@email.com",
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


"""
Classic Cheeseburger:
{
  "title": "Classic Cheeseburger",
  "difficulty": 2,
  "serving_size": 1,
  "instructions": "1. Preheat grill to medium-high heat. 2. Form ground beef into patties and season with salt and pepper. 3. Grill patties for 4-5 minutes on each side, or until desired doneness. 4. Toast hamburger buns on the grill for 1-2 minutes. 5. Assemble burgers with lettuce, tomato, onion, pickles, cheese, ketchup, and mustard. 6. Serve hot and enjoy!",
  "ingredients": [
    { "ingredient": { "name": "ground beef" }, "amount": "200g" },
    { "ingredient": { "name": "hamburger buns" }, "amount": "1" },
    { "ingredient": { "name": "lettuce" }, "amount": "1 leaf" },
    { "ingredient": { "name": "tomato slices" }, "amount": "2" },
    { "ingredient": { "name": "onion slices" }, "amount": "2" },
    { "ingredient": { "name": "pickles" }, "amount": "2 slices" },
    { "ingredient": { "name": "cheddar cheese" }, "amount": "2 slices" },
    { "ingredient": { "name": "ketchup" }, "amount": "to taste" },
    { "ingredient": { "name": "mustard" }, "amount": "to taste" },
    { "ingredient": { "name": "salt" }, "amount": "to taste" },
    { "ingredient": { "name": "black pepper" }, "amount": "to taste" }
  ],
  "allergies": ["gluten", "lactose"]
}
BBQ Pulled Pork Sandwich:
{
  "title": "BBQ Pulled Pork Sandwich",
  "difficulty": 3,
  "serving_size": 1,
  "instructions": "1. Rub pork shoulder with BBQ seasoning and place it in a slow cooker. 2. Cook on low for 8 hours, or until the pork is tender and falls apart easily. 3. Shred the pork using two forks and mix in your favorite BBQ sauce. 4. Toast hamburger buns and assemble sandwiches with the pulled pork. 5. Serve hot and enjoy!",
  "ingredients": [
    { "ingredient": { "name": "pork shoulder" }, "amount": "200g" },
    { "ingredient": { "name": "BBQ seasoning" }, "amount": "to taste" },
    { "ingredient": { "name": "BBQ sauce" }, "amount": "100g" },
    { "ingredient": { "name": "hamburger buns" }, "amount": "1" },
    { "ingredient": { "name": "salt" }, "amount": "to taste" },
    { "ingredient": { "name": "black pepper" }, "amount": "to taste" }
  ],
  "allergies": ["gluten", "lactose"]
}
Macaroni and Cheese:
json
Copy code
{
  "title": "Macaroni and Cheese",
  "difficulty": 2,
  "serving_size": 1,
  "instructions": "1. Cook macaroni according to package instructions. 2. In a saucepan, melt butter and stir in flour to make a roux. 3. Gradually whisk in milk until smooth and thickened. 4. Add shredded cheddar cheese and stir until melted and smooth. 5. Combine cheese sauce with cooked macaroni. 6. Serve hot and enjoy!",
  "ingredients": [
    { "ingredient": { "name": "macaroni" }, "amount": "100g" },
    { "ingredient": { "name": "butter" }, "amount": "30g" },
    { "ingredient": { "name": "flour" }, "amount": "30g" },
    { "ingredient": { "name": "milk" }, "amount": "250ml" },
    { "ingredient": { "name": "cheddar cheese" }, "amount": "100g" },
    { "ingredient": { "name": "salt" }, "amount": "to taste" },
    { "ingredient": { "name": "black pepper" }, "amount": "to taste" }
  ],
  "allergies": ["gluten", "lactose"]
}
Buffalo Chicken Wings:
json
Copy code
{
  "title": "Buffalo Chicken Wings",
  "difficulty": 2,
  "serving_size": 1,
  "instructions": "1. Preheat oven to 400°F (200°C). 2. Season chicken wings with salt and pepper. 3. Bake wings in the preheated oven for 45 minutes, turning once halfway through. 4. In a saucepan, melt butter and mix in hot sauce. 5. Toss baked wings in the sauce until fully coated. 6. Serve with celery sticks and blue cheese dressing.",
  "ingredients": [
    { "ingredient": { "name": "chicken wings" }, "amount": "200g" },
    { "ingredient": { "name": "butter" }, "amount": "50g" },
    { "ingredient": { "name": "hot sauce" }, "amount": "100ml" },
    { "ingredient": { "name": "celery sticks" }, "amount": "2" },
    { "ingredient": { "name": "blue cheese dressing" }, "amount": "to taste" },
    { "ingredient": { "name": "salt" }, "amount": "to taste" },
    { "ingredient": { "name": "black pepper" }, "amount": "to taste" }
  ],
  "allergies": ["gluten"]
}

"""
