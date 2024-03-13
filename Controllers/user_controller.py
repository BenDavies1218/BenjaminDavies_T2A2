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
        body_data = request.get_json()

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
            return {"error": f"The {err.orig.diag.column_name} is required"}
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409


@db_auth.route("/login", methods=["POST"])  # /auth/login
def auth_login():
    # get the data from the request body
    body_data = request.get_json()
    # Find the user with the email address
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # If user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create jwt
        token = create_access_token(
            identity=str(user.id), expires_delta=timedelta(days=21)
        )
        # return the token along with the user info
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    # else
    else:
        # return error
        return {"error": "Invalid email or password"}, 401


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - READ


@db_auth.route("/user")
@jwt_required()
@authorise_as_admin
def get_all_users():
    stmt = db.select(User)
    users = db.session.scalars(stmt)
    if not users:
        return {"error": "no users could be found"}, 404
    return users_schema.dump(users)


@db_auth.route("/user/<int:user_id>")
@jwt_required()
@user_owner
def get_one_user(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return {"error": f"User with id {user_id} couldn't be found"}, 404
    return user_schema.dump(user)


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - UPDATE

@db_auth.route("/user/update/<int:user_id>", methods=["POST"])
@jwt_required()
@user_owner
def user_update(user_id):
    

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# CRUD - DELETE
