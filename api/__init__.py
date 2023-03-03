# db must be initialized before importing models
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
