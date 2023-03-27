from api.user.author.docs import author_schema

comment_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "comment"},
        "author": author_schema,
        "comment": {"type": "string", "example": "First"},
        "contentType": {"type": "string", "example": "text/plain"},
        "published": {"type": "string", "example": "2015-03-09T13:07:04+00:00"},
        "id": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss/comments/saxkn2342dfsasd",
        },
    },
}

comments_schema = {
    "properties": {
        "type": {"type": "string", "example": "comments"},
        "page": {"type": "integer", "example": 1},
        "size": {"type": "integer", "example": 5},
        "post": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss",
        },
        "id": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss/comments",
        },
        "comments": {"type": "array", "items": comment_schema},
    }
}
