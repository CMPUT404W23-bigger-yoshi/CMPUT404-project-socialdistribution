from dataclasses import dataclass

from api import db


@dataclass
class Connection(db.Model):
    username: str = db.Column(db.Text, primary_key=True)
    password: str = db.Column(db.Text, nullable=False)
