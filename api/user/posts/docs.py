from api.user.author.docs import *
from api.user.comments.docs import *
from api.user.followers.docs import *

post_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "post"},
        "title": {"type": "string", "example": "Found a new recipe"},
        "source": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com"},
        "origin": {"type": "string", "example": "https://bigger-yoshi-herokuapp.com"},
        "description": {"type": "string", "example": "Easy 10 minutes recipe"},
        "content": {"type": "string", "example": "An apple a day keeps the doctor away."},
        "categories": {"type": "array", "items": {"type": "string", "example": "Food"}},
        "count": {"type": "integer", "example": 1},
        "author": author_schema,
        "comments": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss/comments",
        },
        "contentType": {"type": "string", "example": "text/plain"},
        "published": {"type": "string", "example": "2015-03-09T13:07:04+00:00"},
        "visibility": {"type": "string", "enum": ["PUBLIC", "FRIENDS"]},
        "unlisted": {"type": "boolean", "example": "false"},
        "id": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss",
        },
    },
}

posts_schema = {
    "properties": {
        "type": {"type": "string", "example": "posts"},
        "page": {"type": "integer", "example": 5},
        "size": {"type": "integer", "example": 5},
        "items": {"type": "array", "items": post_schema},
    }
}

inbox_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "inbox"},
        "author": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com/authors/92seGh3Kskw22-ee789"},
        "items": {"type": "array", "items": {"oneOf": [post_schema, comment_schema]}},
    },
}

like_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "like"},
        "author": author_schema,
        "object": {
            "type": "string",
            "example": "https://bigger-yoshi.herokuapp.com/authors/69abdhgtT420wjsw/posts/404htyrien212ss",
        },
        "summary": {"type": "string", "example": "John Wick likes your post"},
    },
}

likes_schema = {
    "properties": {"type": {"type": "string", "example": "likes"}, "items": {"type": "array", "items": like_schema}}
}

follow_schema = {
    "properties": {
        "type": {"type": "string", "example": "Follow"},
        "summary": {"type": "string", "example": "Greg wants to follow John Wick"},
        "actor": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "example": "author"},
                "id": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com/authors/21jHyoh21nnd893sals"},
                "host": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com"},
                "displayName": {"type": "string", "example": "Greg Johnson"},
                "url": {"type": "string", "example": "https://bigger-yoshi.herokuapp.com/authors/21jHyoh21nnd893sals"},
                "github": {"type": "string", "example": "http://github.com/gjohnson"},
                "profileImage": {"type": "string", "example": "https://i.imgur.com/k7XVwpB.jpeg"},
            },
        },
        "object": author_schema,
    }
}
