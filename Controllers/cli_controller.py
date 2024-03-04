from datetime import date
from seeding_function import seed
from flask import Blueprint
from init import db, bcrypt
from Models.user import User
from Models.review import Review

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
    users, reviews = seed()
    db.session.add_all(users)
    db.session.add_all(reviews)

    db.session.commit()

    print("Tables seeded")
