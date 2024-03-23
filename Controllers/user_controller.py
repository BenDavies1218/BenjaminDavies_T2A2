from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required
from psycopg2 import errorcodes

from Functions.Decorator_functions import authorise_as_admin, user_owner
from init import db, bcrypt
from Models.user import User, user_schema, users_schema

db_auth = Blueprint("auth", __name__, url_prefix="/auth")


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# CRUD - CREATE


@db_auth.route("/register", methods=["POST"])
def auth_register():
    try:
        # the data that we get in body of the request
        body_data = user_schema.load(request.get_json())

        # create the user instance
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email"),
            is_admin=body_data.get("is_admin"),
        )

        # password from the request body
        password = body_data.get("password")
        # if password exists, hash the password
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        # add and commit the user to DB
        db.session.add(user)
        db.session.commit()
        # Repond back to the client
        return user_schema.dump(user), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409


@db_auth.route("/login", methods=["POST"])  # /auth/login
def auth_login():
    try:
        # get the data from the request body
        body_data = user_schema.load(request.get_json())

        # Queries database for user with email in POST request returns all data on that user
        stmt = db.select(User).filter_by(email=body_data.get("email"))
        user = db.session.scalar(stmt)
        # If user exists and password is correct
        if user and bcrypt.check_password_hash(
            user.password, body_data.get("password")
        ):
            # creates a JWT token i set the timedelta to 21 days so i didn't have to login my user in everytime i wanted to test an endpoint
            token = create_access_token(
                identity=str(user.id), expires_delta=timedelta(days=21)
            )
            # return the token along with the user info
            return {"email": user.email, "token": token, "is_admin": user.is_admin}
        # else
        else:
            # return error
            return {"error": "Invalid email or password"}, 401

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@db_auth.route("/user")
@jwt_required()
@authorise_as_admin
def get_all_users():
    # queries the database from all the rows in the table user returns all the data on each user
    stmt = db.select(User)
    users = db.session.scalars(stmt)
    # if no users exist we send an error
    if not users:
        return {"error": "no users could be found"}, 404
    # return the users
    return users_schema.dump(users)


@db_auth.route("/user/<int:user_id>")
@jwt_required()
@user_owner
def get_one_user(user_id):
    # Query database for the user with there id equal to the argument passed into the function
    user = db.session.query(User).filter_by(id=user_id).first()
    # if the user can't be found send a message back
    if not user:
        return {"error": f"User with id {user_id} couldn't be found"}, 404
    # return the users information
    return user_schema.dump(user)


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE


@db_auth.route("/user/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@user_owner
def user_update(user_id):
    try:
        # load the users data with, sanitize with the schema
        body_data = user_schema.load(request.get_json(), partial=True)
        # query the database for the user with id that is passed into function
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        password = body_data.get("password")
        if password:
            password = bcrypt.generate_password_hash(password).decode("utf-8")
            db.session.commit()
        if user:
            user.name = body_data.get("name") or user.name
            user.email = body_data.get("email") or user.email
            user.password = password or user.password
            user.is_admin = body_data.get("is_admin") or user.is_admin
            db.session.commit()
            return user_schema.dump(user)
        else:
            # return error msg
            return {"error": f"User with id {user_id} not found"}, 404

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 400

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE


@db_auth.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@user_owner
def delete_user(user_id):
    # query the database for the user with target id
    user = db.session.query(User).filter_by(id=user_id).first()
    # if the user cannot be found give an error
    if not user:
        return {"error": f"User with id {user_id} couldn't be found"}, 404
    db.session.delete(user)
    db.session.commit()
    # user successfully deleted
    return {"message": f"User with id {user_id} successfully deleted"}, 200
