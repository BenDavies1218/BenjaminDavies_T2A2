import functools
from Models.user import User
from init import db
from flask_jwt_extended import get_jwt_identity


# this decorator is used when an action can ONLY be performed by an administator
def authorise_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)

        # If the user is not found
        if not user:
            return {
                "error": "Failure to authorize user.id doesn't match Please check your token"
            }, 404

        # if the user is an admin
        if user.is_admin:
            # we will continue and run the decorated function
            return fn(*args, **kwargs)
        # else (if the user is NOT an admin)
        else:
            # return an error
            return {"error": "Not authorised to request this"}, 403

    return wrapper


# This decorator is used when an action can only be performed by a specific user or administator as administators by default have the highest level of authorization
def user_owner(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = db.session.query(User).filter_by(id=user_id).first()

        # If the user is not found
        if not user:
            return {
                "error": "Failure to authorize user.id doesn't match Please check your token"
            }, 404

        # Check if the user is the owner or an admin we can continue with the request
        if user.id == kwargs.get("user_id") or user.is_admin == True:
            return fn(*args, **kwargs)
        else:
            return {"error": "Not authorized to request this"}, 403

    return wrapper
