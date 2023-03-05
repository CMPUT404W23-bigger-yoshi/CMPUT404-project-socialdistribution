"""Flask configuration."""
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base config."""

    SECRET_KEY = environ.get("SECRET_KEY")
    # not sure why, but this default value puts it in instance/bigger_yoshi.db. Not just the bare file as expected
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///bigger_yoshi.db")
    BCRYPT_LOG_ROUNDS = 13
