author_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "author"},
        "id": {
            "type": "string",
        },
        "host": {
            "type": "string",
        },
        "displayName": {
            "type": "string",
        },
        "url": {
            "type": "string",
        },
        "github": {
            "type": "string",
        },
        "profileImage": {
            "type": "string",
        },
    },
}

authors_schema = {
    "properties": {"type": {"type": "string", "example": "authors"}, "items": {"type": "array", "items": author_schema}}
}
