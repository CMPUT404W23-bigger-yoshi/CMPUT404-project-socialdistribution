from api.app import db

author_likes_comments = db.Table(
    db.Column("auth_id", db.Integer, db.ForeignKey("author.id")),
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
)

author_likes_posts = db.Table(
    db.Column("auth_id", db.Integer, db.ForeignKey("author.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)
