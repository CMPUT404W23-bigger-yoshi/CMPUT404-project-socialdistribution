# db must be initialized before importing models
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

# Temporarily using sqlite right now
engine = create_engine("sqlite:///bigger_yoshi.db")
