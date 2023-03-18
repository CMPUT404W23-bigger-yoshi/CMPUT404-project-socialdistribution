"""Flask configuration."""
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base config."""

    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI", environ.get("DATABASE_URL", "")).replace(
        "postgres://", "postgresql://"
    )
    BCRYPT_LOG_ROUNDS = 13
    BASIC_AUTH_REALM = "Bigger-Yoshi"
    FLASK_ADMIN_SWATCH = "cerulean"
    BASIC_AUTH_FORCE = True
    SELF_USERNAME = environ.get("SELF_AUTH_USERNAME")
    SELF_PASSWORD = environ.get("SELF_AUTH_PASSWORD")
