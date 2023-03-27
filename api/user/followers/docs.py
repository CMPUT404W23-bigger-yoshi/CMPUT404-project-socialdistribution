from api.user.author.docs import author_schema

followers_schema = {
    "properties": {
        "type": {"type": "string", "example": "followers"},
        "items": {"type": "array", "items": author_schema},
    }
}
