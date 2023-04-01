# db must be initialized before importing models
import logging
from pathlib import Path

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
API_ROOT = "/api"

from api.admin.APIAuth import APIAuth

basic_auth = APIAuth()

module_root = Path(__file__).parent.name
logger = logging.getLogger(module_root)

stdout_handler = logging.StreamHandler()
# (matt) small personal preference: warning -> warn (better alignment of text in the logs :)
logging.addLevelName(logging.WARNING, "WARN")
formatter = logging.Formatter(
    "{asctime} [{levelname}] {module}:{lineno} {message}", style="{", datefmt="%Y-%m-%dT%H:%M:%S%z"
)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

stdout_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
