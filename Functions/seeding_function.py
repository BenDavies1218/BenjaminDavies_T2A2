from Models.user import User
from Models.review import Review
from Models.ingredient import Ingredient
from Models.recipe import Recipe
from Models.allergy import Allergy
from Models.recipe_allergies import RecipeAllergy
from Models.recipe_ingredients import RecipeIngredient
from init import bcrypt


def seed_data():
    users = [
        User(
            name="Simon",
            email="Simon@email.com",
            password=bcrypt.generate_password_hash("Coderacademy1!").decode("utf-8"),
            is_admin=True,
        ),
        User(
            name="Ben",
            email="ben@email.com",
            password=bcrypt.generate_password_hash("Coderacademy1!").decode("utf-8"),
        ),
        User(
            name="luis",
            email="luis@email.com",
            password=bcrypt.generate_password_hash("Coderacademy1!").decode("utf-8"),
        ),
        User(
            name="dan",
            email="dan@email.com",
            password=bcrypt.generate_password_hash("Coderacademy1!").decode("utf-8"),
        ),
        User(
            name="jairo",
            email="jairo@email.com",
            password=bcrypt.generate_password_hash("Coderacademy1!").decode("utf-8"),
        ),
    ]
    recipes = [
        Recipe(
            title="CheeseBurger",
            user_id=1,
            difficulty=2,
            serving_size=1,
            instructions="1. Preheat grill to medium-high heat. 2. Form ground beef into patties and season with salt and pepper. 3. Grill patties for 4-5 minutes on each side, or until desired doneness. 4. Toast hamburger buns on the grill for 1-2 minutes. 5. Assemble burgers with lettuce, tomato, onion, pickles, cheese, ketchup, and mustard. 6. Serve hot and enjoy!",
        ),
        Recipe(
            title="BBQ Pulled Pork Sandwich",
            user_id=2,
            difficulty=3,
            serving_size=1,
            instructions="1. Rub pork shoulder with BBQ seasoning and place it in a slow cooker. 2. Cook on low for 8 hours, or until the pork is tender and falls apart easily. 3. Shred the pork using two forks and mix in your favorite BBQ sauce. 4. Toast hamburger buns and assemble sandwiches with the pulled pork. 5. Serve hot and enjoy!",
        ),
        Recipe(
            title="Macaroni and Cheese",
            user_id=3,
            difficulty=2,
            serving_size=1,
            instructions="1. Cook macaroni according to package instructions. 2. In a saucepan, melt butter and stir in flour to make a roux. 3. Gradually whisk in milk until smooth and thickened. 4. Add shredded cheddar cheese and stir until melted and smooth. 5. Combine cheese sauce with cooked macaroni. 6. Serve hot and enjoy!",
        ),
        Recipe(
            title="Buffalo Chicken Wings",
            user_id=4,
            difficulty=2,
            serving_size=1,
            instructions="1. Preheat oven to 400°F (200°C). 2. Season chicken wings with salt and pepper. 3. Bake wings in the preheated oven for 45 minutes, turning once halfway through. 4. In a saucepan, melt butter and mix in hot sauce. 5. Toss baked wings in the sauce until fully coated. 6. Serve with celery sticks and blue cheese dressing.",
        ),
    ]

    # Ingredient information
    ingredients_list = [
        "ground beef",
        "hamburger buns",
        "lettuce",
        "tomato slices",
        "onion slices",
        "pickles",
        "cheddar cheese",
        "ketchup",
        "mustard",
        "salt",
        "black pepper",
        "pork shoulder",
        "BBQ seasoning",
        "BBQ sauce",
        "macaroni",
        "flour",
        "milk",
        "chicken wings",
        "butter",
        "hot sauce",
        "celery sticks",
        "blue cheese dressing",
    ]
    ingredients = [Ingredient(name=name) for name in ingredients_list]

    # adding alleries using a for loop and list to create each allergy instance
    allergies_list = ["Pork", "Dairy", "Gluten"]
    allergies = [Allergy(name=name) for name in allergies_list]

    # Looks a bit crazy but didn't take too long.
    recipes_relations = [
        {"recipe": recipes[0], "ingredient": ingredients[0], "amount": "200gm"},
        {"recipe": recipes[0], "ingredient": ingredients[1], "amount": "1"},
        {"recipe": recipes[0], "ingredient": ingredients[2], "amount": "1 leaf"},
        {"recipe": recipes[0], "ingredient": ingredients[3], "amount": "2"},
        {"recipe": recipes[0], "ingredient": ingredients[4], "amount": "2"},
        {"recipe": recipes[0], "ingredient": ingredients[5], "amount": "2 slices"},
        {"recipe": recipes[0], "ingredient": ingredients[6], "amount": "2 slices"},
        {"recipe": recipes[0], "ingredient": ingredients[7], "amount": "to taste"},
        {"recipe": recipes[0], "ingredient": ingredients[8], "amount": "to taste"},
        {"recipe": recipes[0], "ingredient": ingredients[9], "amount": "to taste"},
        {"recipe": recipes[0], "ingredient": ingredients[10], "amount": "to taste"},
        {"recipe": recipes[1], "ingredient": ingredients[11], "amount": "200gm"},
        {"recipe": recipes[1], "ingredient": ingredients[12], "amount": "20gm"},
        {"recipe": recipes[1], "ingredient": ingredients[13], "amount": "20gm"},
        {"recipe": recipes[1], "ingredient": ingredients[1], "amount": "1"},
        {"recipe": recipes[1], "ingredient": ingredients[9], "amount": "to taste"},
        {"recipe": recipes[1], "ingredient": ingredients[10], "amount": "to taste"},
        {"recipe": recipes[2], "ingredient": ingredients[14], "amount": "300gm"},
        {"recipe": recipes[2], "ingredient": ingredients[18], "amount": "50gm"},
        {"recipe": recipes[2], "ingredient": ingredients[15], "amount": "1 cup"},
        {"recipe": recipes[2], "ingredient": ingredients[16], "amount": "200ml"},
        {"recipe": recipes[2], "ingredient": ingredients[6], "amount": "100gm"},
        {"recipe": recipes[2], "ingredient": ingredients[9], "amount": "to taste"},
        {"recipe": recipes[2], "ingredient": ingredients[10], "amount": "to taste"},
        {"recipe": recipes[3], "ingredient": ingredients[17], "amount": "200gm"},
        {"recipe": recipes[3], "ingredient": ingredients[18], "amount": "50gm"},
        {"recipe": recipes[3], "ingredient": ingredients[19], "amount": "100ml"},
        {"recipe": recipes[3], "ingredient": ingredients[20], "amount": "2"},
        {"recipe": recipes[3], "ingredient": ingredients[21], "amount": "to taste"},
        {"recipe": recipes[3], "ingredient": ingredients[9], "amount": "to taste"},
        {"recipe": recipes[3], "ingredient": ingredients[10], "amount": "to taste"},
    ]

    # Using a for loop with the unpack operator to create each instance of the recipe ingredient.
    recipe_ingredients = [RecipeIngredient(**data) for data in recipes_relations]

    allergy_relations = [
        {"recipe": recipes[0], "allergy": allergies[1]},
        {"recipe": recipes[0], "allergy": allergies[2]},
        {"recipe": recipes[1], "allergy": allergies[0]},
        {"recipe": recipes[1], "allergy": allergies[1]},
        {"recipe": recipes[1], "allergy": allergies[2]},
        {"recipe": recipes[2], "allergy": allergies[1]},
        {"recipe": recipes[2], "allergy": allergies[2]},
        {"recipe": recipes[3], "allergy": allergies[2]},
    ]

    # Using a for loop with the unpack operator to create each instance of the recipe allergy.
    recipe_allergies = [RecipeAllergy(**data) for data in allergy_relations]

    review_data = [
        {
            "details": "The Cheeseburger recipe exceeded all expectations! The grilled ground beef patty was juicy and flavorful, perfectly complemented by the fresh toppings and melted cheddar cheese. The instructions were clear and easy to follow, resulting in a restaurant-quality burger that I'll definitely be making again.",
            "rating": 10,
            "user_id": 3,
            "recipe_id": 1,
        },
        {
            "details": "I was highly disappointed with the Cheeseburger recipe. The burger patty was dry and lacked seasoning, and the toppings felt uninspired. Despite following the instructions carefully, the end result was a bland and forgettable burger. I won't be making this recipe again.",
            "rating": 2,
            "user_id": 2,
            "recipe_id": 1,
        },
        {
            "details": "The BBQ Pulled Pork Sandwich recipe was alright. The pork shoulder was tender, but I found the BBQ sauce to be a bit too overpowering. It masked the flavor of the meat, making it hard to fully enjoy. It's a decent recipe, but it could use some adjustments.",
            "rating": 1,
            "user_id": 1,
            "recipe_id": 2,
        },
        {
            "details": "I regret trying the BBQ Pulled Pork Sandwich recipe. The pork shoulder turned out tough and dry, and the BBQ sauce lacked depth of flavor. Despite following the instructions meticulously, the end result was disappointing. I won't be making this recipe again.",
            "rating": 2,
            "user_id": 4,
            "recipe_id": 2,
        },
        {
            "details": "The Macaroni and Cheese recipe was phenomenal! The cheese sauce was creamy and decadent, coating the perfectly cooked macaroni in a blanket of cheesy goodness. Each bite was pure comfort, and it quickly became a household favorite. This recipe is an absolute winner!",
            "rating": 9,
            "user_id": 5,
            "recipe_id": 3,
        },
        {
            "details": "The Macaroni and Cheese recipe was decent. The cheese sauce was creamy, but I found the dish to be a bit bland overall. It lacked that extra something to make it truly stand out. It's a satisfactory mac and cheese recipe, but nothing extraordinary.",
            "rating": 7,
            "user_id": 1,
            "recipe_id": 3,
        },
        {
            "details": "The Buffalo Chicken Wings recipe was a hit! The chicken wings were perfectly crispy, and the buffalo sauce had just the right amount of heat. Paired with celery sticks and blue cheese dressing, it was a flavor explosion that left everyone wanting more. This recipe is a definite keeper!",
            "rating": 10,
            "user_id": 3,
            "recipe_id": 4,
        },
        {
            "details": "The Buffalo Chicken Wings were decent. The chicken wings were crispy, but I found the buffalo sauce to be a bit lacking in flavor. It needed more depth to truly elevate the dish. Overall, it's a passable recipe, but there's room for improvement.",
            "rating": 6,
            "user_id": 1,
            "recipe_id": 4,
        },
    ]

    reviews = [Review(**data) for data in review_data]

    return (
        users,
        recipes,
        ingredients,
        allergies,
        recipe_ingredients,
        recipe_allergies,
        reviews,
    )
