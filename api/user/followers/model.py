from dataclasses import dataclass


@dataclass
class Follower:
    type: str
    id: str
    url: str
    host: str
    displayName: str
    github: str
    profileImage: str


def create_follower(follower_to_add: Follower):
    pass


def delete_follower(author_id: str, follower_id: str):
    pass


def get_followers(author_id: str):
    pass


def add_follower(author_id: str, follower_to_add: str):
    pass


# todo: discuss what this is?
# GET [local, remote] check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
