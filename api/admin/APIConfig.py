"""API configuration."""
from os import environ, path

from dotenv import load_dotenv, set_key

basedir = path.abspath(path.dirname(__file__))
path_to_env = path.join(basedir, "../.env")
load_dotenv(path_to_env)


class APIConfig:
    """Base config."""

    BASIC_AUTH_REALM = "Bigger-Yoshi"
    SELF_USERNAME = environ.get("SELF_AUTH_USERNAME")
    SELF_PASSWORD = environ.get("SELF_AUTH_PASSWORD")

    @staticmethod
    def set_node_limit(limit: int):
        set_key(path_to_env, "NODE_LIMIT", str(limit))

    @staticmethod
    def set_author_approval(val: bool):
        set_key(path_to_env, "AUTHOR_AUTO_APPROVAL", str(val))

    @staticmethod
    def set_API_protection(val: bool):
        set_key(path_to_env, "BASIC_AUTH_FORCE", str(val))

    @staticmethod
    def set_node_approval(val: bool):
        set_key(path_to_env, "NODE_AUTO_APPROVAL", str(val))

    @property
    def is_API_protected():
        load_dotenv(path_to_env)
        return True if environ.get("BASIC_AUTH_FORCE").lower() == "true" else False

    @property
    def connection_approval():
        load_dotenv(path_to_env)
        return True if environ.get("NODE_AUTO_APPROVAL").lower() == "true" else False

    @property
    def author_approval():
        load_dotenv(path_to_env)
        return True if environ.get("AUTHOR_AUTO_APPROVAL").lower() == "true" else False

    @property
    def node_limit():
        load_dotenv(path_to_env)
        return int(environ.get("NODE_LIMIT"))
