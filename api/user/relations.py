from api import db

# todo sqlalchemy docs use meta with tables? idk why. will also need a table name i think

author_likes_comments = db.Table(
    "comment_like",
    db.Column("author", db.Text, primary_key=True),
    db.Column("comment", db.Text, primary_key=True),
)

author_likes_posts = db.Table(
    "post_like",
    db.Column("author", db.Text, primary_key=True),
    db.Column("post", db.Text, primary_key=True),
)

post_images = db.Table(
    "post_images",
    db.Column("post_id", db.String(200), db.ForeignKey("post.id")),
    db.Column("image", db.Text, nullable=False),
)
