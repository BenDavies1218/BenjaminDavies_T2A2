import os
from flask import Flask
from init import db, ma, bcrypt, jwt, migrate
from marshmallow.exceptions import ValidationError


def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False

    # configs
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    @app.errorhandler(ValidationError)
    def validation_error(error):
        return {"error": error.messages}, 400

    @app.errorhandler(400)
    def bad_request(err):
        return {"error": str(err)}, 400

    @app.errorhandler(401)
    def not_authorized(err):
        return {"error": str(err)}, 401

    @app.errorhandler(404)
    def bad_request(err):
        return {"error": str(err)}, 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return {"error": str(err)}, 405

    @app.errorhandler(500)
    def server_error(err):
        return {"error": str(err)}, 500

    # connect libraries with flask app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from Controllers.cli_controller import db_commands
    from Controllers.recipe_controller import db_recipes
    from Controllers.user_controller import db_auth
    from Controllers.review_controller import review_bp
    from Controllers.ingredient_controller import ingredient_bp
    from Controllers.allergy_controller import allergy_bp

    app.register_blueprint(db_commands)
    app.register_blueprint(db_recipes)
    app.register_blueprint(db_auth)
    app.register_blueprint(review_bp)
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(allergy_bp)

    @app.route("/")
    def index():
        return "Hello and welcome to my recipe api!"

    return app
