# db must be initialized before importing models
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

from api.admin.APIAuth import APIAuth

basic_auth = APIAuth()
