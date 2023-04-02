# db must be initialized before importing models
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

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

# some params that are used around the app
API_PATH = "/api"
load_dotenv()
DEFAULT_API_BASE = "https://bigger-yoshi.herokuapp.com/api/"
API_BASE = os.getenv("API_BASE")  # must be set manually on heroku
if API_BASE is None:
    logger.info(f"falling back to default API base since API_BASE wasn't set: {DEFAULT_API_BASE}")
    API_BASE = DEFAULT_API_BASE
else:
    logger.info(f"found API_BASE: {API_BASE}")

parsed_base = urlparse(API_BASE)
API_HOSTNAME = parsed_base.hostname

load_dotenv(Path(__file__).parent / ".env")
