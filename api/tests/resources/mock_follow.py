mock_follow_request = {
    "type": "Follow",
    "summary": "Greg wants to follow Lara",
    "actor": {
        "type": "author",
        "id": "http://127.0.0.1:5000/authors/1d698d25ff008f7538453c120f581471",
        "url": "http://127.0.0.1:5000/authors/1d698d25ff008f7538453c120f581471",
        "host": "http://127.0.0.1:5000/",
        "displayName": "Greg Johnson",
        "github": "http://github.com/gjohnson",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    },
    "object": {
        "type": "author",
        # ID of the Author
        "id": "http://127.0.0.1:5000/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        # the home host of the author
        "host": "http://127.0.0.1:5000/",
        # the display name of the author
        "displayName": "Lara Croft",
        # url to the authors profile
        "url": "http://127.0.0.1:5000/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        # HATEOS url for Github API
        "github": "http://github.com/laracroft",
        # Image from a public domain
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    },
}
