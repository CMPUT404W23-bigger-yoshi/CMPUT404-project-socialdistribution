from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Post(db.Model):
    _id = db.Column("post_id", db.Integer, primary_key=True)
    published = db.Column("published", db.DateTime, nullable=False)
    title = db.Column("title", db.String, nullable=False)
    origin = db.Column("origin", db.String, nullable=False)
    source = db.Column("source", db.String, nullable=False)
    description = db.Column("short_desc", db.String)
    contentType = db.Column("contentType", db.String, nullable=False)
    content = db.Column("content", db.String, nullable=False)

    # categories will be comma separated values
    categories = db.Column("categories", db.String)

    # 0 -> "PUBLIC", 1-> "FRIENDS"
    visibility = db.Column("visibility", db.Boolean, nullable=False)

    # 0 -> False, 1 -> True
    unlisted = db.Column("unlisted", db.Boolean, nullable=False)

    def __init__(self):
        pass

    def __repr__(self):
        return f"<Author: {{'id': {self.id}, }}>"
