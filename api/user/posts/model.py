from dataclasses import asdict, dataclass
from datetime import datetime

from sqlalchemy import Enum, event

from api.app import db
from api.user.author.model import Author
from api.utils import Visibility, generate_object_ID, get_pagination_params


@dataclass
class Post(db.Model):
    # TODO might need to change id length to accomodate other teams id
    id: str = db.Column(db.String(50), primary_key=True, default=generate_object_ID)
    object_id: str = db.Column(db.String(50), nullable=True)
    published: str = db.Column("published", db.String(20), nullable=False)
    title: str = db.Column("title", db.String(120), nullable=False)
    origin: str = db.Column("origin", db.Text, nullable=False)
    source: str = db.Column("source", db.Text, nullable=False)
    description: str = db.Column("short_desc", db.String(100))
    contentType: str = db.Column("contentType", db.String(50), nullable=False)
    content: str = db.Column("content", db.Text, nullable=False)
    # categories will be comma separated values
    categories: str = db.Column("categories", db.Text)

    # 0 -> "PUBLIC", 1-> "FRIENDS"
    visibility: Visibility = db.Column("visibility", Enum(Visibility), nullable=False, default=Visibility.PUBLIC)

    unlisted: bool = db.Column("unlisted", db.Boolean, nullable=False, default=False)

    # Foreign Key
    inbox: str = db.Column("inbox", db.String(50), db.ForeignKey("author.id"), primary_key=True, nullable=False)

    # Complete URL of the author
    author_id: str = db.Column("author_id", db.String(50), nullable=False)

    # Relationships -> lazy = "dynamic" returns a query object to further refine.
    comments = db.relationship(
        "Comment", backref="post", lazy="dynamic", cascade="all, delete"
    )  # what will be the type of this?

    # TODO Images

    def getJSON(self) -> dict:
        post = asdict(self)
        post["type"] = "post"

        # Setting author
        author = Author.query.filter_by(id=post["author_id"]).first()
        post["author"] = author.getJSON()
        del post["author_id"]

        # Categories
        if post["categories"]:
            post["categories"] = post["categories"].split(",")

        # Visibility
        if post["visibility"] == Visibility.PUBLIC:
            post["visibility"] = "PUBLIC"
        elif post["visibility"] == Visibility.FRIENDS:
            post["visibility"] = "FRIENDS"

        # Comments
        post["count"] = len(self.comments.all())
        comments_url = post["id"] + "/comments"
        post["comments"] = comments_url

        commentSrc = {}
        commentSrc["type"] = "comments"
        pages = get_pagination_params().page
        commentSrc["page"] = pages
        size = get_pagination_params().size
        commentSrc["size"] = size
        commentSrc["post"] = post["id"]
        commentSrc["id"] = comments_url

        # TODO jsonify comments correctly here
        commentSrc["comments"] = self.comments.paginate(page=pages, per_page=size).items

        post["commentSrc"] = commentSrc
        del post["inbox"]
        return post

    def __repr__(self) -> str:
        return f"<Post {self.id} author={self.author_id} title={self.title}>"


@event.listens_for(Post, "after_insert")
def post_after_insert(mapper, connection, target):
    post_table = Post.__table__
    primary_id = target.id

    post_complete_url = target.author_id + "/posts/" + primary_id

    modify_id = (
        post_table.update().where(post_table.c.id == primary_id).values(id=post_complete_url, object_id=primary_id)
    )
    connection.execute(modify_id)
