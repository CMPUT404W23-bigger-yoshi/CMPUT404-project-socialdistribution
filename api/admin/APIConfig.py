"""API configuration."""
from os import environ, path

from dotenv import load_dotenv, set_key
from flask import current_app

basedir = path.abspath(path.dirname(__file__))
path_to_env = path.join(basedir, "../.env")
load_dotenv(path_to_env)


class APIConfig:
    """Base config."""

    BASIC_AUTH_REALM = "Bigger-Yoshi"
    SELF_USERNAME = environ.get("SELF_AUTH_USERNAME")
    SELF_PASSWORD = environ.get("SELF_AUTH_PASSWORD")
    NODE_AUTO_APPROVAL = environ.get("NODE_AUTO_APPROVAL").lower() == "true"
    AUTHOR_AUTO_APPROVAL = environ.get("AUTHOR_AUTO_APPROVAL").lower() == "true"
    NODE_LIMIT = int(environ.get("NODE_LIMIT"))

    @classmethod
    def reload(self):
        self.SELF_USERNAME = environ.get("SELF_AUTH_USERNAME")
        self.SELF_PASSWORD = environ.get("SELF_AUTH_PASSWORD")
        self.NODE_AUTO_APPROVAL = environ.get("NODE_AUTO_APPROVAL").lower() == "true"
        self.AUTHOR_AUTO_APPROVAL = environ.get("AUTHOR_AUTO_APPROVAL").lower() == "true"
        self.NODE_LIMIT = int(environ.get("NODE_LIMIT"))

    @staticmethod
    def set_node_limit(limit: int):
        set_key(path_to_env, "NODE_LIMIT", str(limit))

    @staticmethod
    def set_author_approval(val: bool):
        set_key(path_to_env, "AUTHOR_AUTO_APPROVAL", str(val))

    @staticmethod
    def set_API_protection(val: bool):
        current_app.config.update({"BASIC_AUTH_FORCE": val})
        set_key(path_to_env, "BASIC_AUTH_FORCE", str(val))

    @staticmethod
    def set_node_approval(val: bool):
        set_key(path_to_env, "NODE_AUTO_APPROVAL", str(val))
