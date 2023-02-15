from api.app import db

# todo sqlalchemy docs use meta with tables? idk why. will also need a table name i think

author_likes_comments = db.Table(
    "comment_like",
    db.Column("author_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id"), primary_key=True),
)

author_likes_posts = db.Table(
    "post_like",
    db.Column("author_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)
