author_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "author"},
        "id": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw"},
        "host": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com"},
        "displayName": {"type": "string", "example": "John Wick"},
        "url": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw"},
        "github": {"type": "string", "example": "http://github.com/babayaga"},
        "profileImage": {"type": "string", "example": "https://i.imgur.com/k7XVwpB.jpeg"},
    },
}

authors_schema = {
    "properties": {"type": {"type": "string", "example": "authors"}, "items": {"type": "array", "items": author_schema}}
}
