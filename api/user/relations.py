from api.app import db

author_comments = db.Table(
    db.Column("auth_id", db.Integer, db.ForeignKey("author.id")),
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
)

author_posts = db.Table(
    db.Column("auth_id", db.Integer, db.ForeignKey("author.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)
