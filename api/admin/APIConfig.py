"""API configuration."""
import logging
from os import environ, path

from dotenv import load_dotenv
from flask import current_app

basedir = path.abspath(path.dirname(__file__))
path_to_env = path.join(basedir, "../.env")
load_dotenv(path_to_env)

logger = logging.getLogger(__name__)


class APIConfig:
    """Base config."""

    IS_API_PROTECTED = False
    NODE_AUTO_APPROVE = True
    AUTHOR_AUTO_APPROVE = False
    NODE_LIMIT = 100

    @classmethod
    def set_node_limit(self, limit: int):
        self.NODE_LIMIT = limit

    @classmethod
    def set_author_approval(self, val: bool):
        self.AUTHOR_AUTO_APPROVE = val

    @classmethod
    def set_API_protection(self, val: bool):
        current_app.config.update({"BASIC_AUTH_FORCE": val})
        self.IS_API_PROTECTED = val

    @classmethod
    def set_node_approval(self, val: bool):
        self.NODE_AUTO_APPROVE = val
