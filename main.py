import os
from flask import Flask
from init import db, ma, bcrypt, jwt
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

    @app.errorhandler(404)
    def bad_request(err):
        return {"error": str(err)}, 404

    # connect libraries with flask app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from Controllers.cli_controller import db_commands
    from Controllers.recipe_controller import db_recipes
    from Controllers.user_controller import db_auth

    app.register_blueprint(db_commands)
    app.register_blueprint(db_recipes)
    app.register_blueprint(db_auth)

    @app.route("/")
    def index():
        doc_string = """
        Hello and welcome to my recipe application the endpoints for the application are as follows:
        """
        return doc_string

    return app
