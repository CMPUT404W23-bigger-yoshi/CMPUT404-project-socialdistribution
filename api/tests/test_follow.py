import pytest

from api import API_ROOT
from api.tests.resources.mock_authors import *
from api.tests.resources.mock_follow import *
from api.user.author.model import Author


class TestFollow:
    @pytest.fixture
    def register_mock_authors(client):
        client.post(f"{API_ROOT}/authors/register", json={"username": mock_author1["displayName"], "password": "test"})
        client.post(f"{API_ROOT}/authors/register", json={"username": mock_author2["displayName"], "password": "test"})

    @pytest.fixture
    def send_local_follow(register_mock_authors, client):
        client.post()

    """
    Test get all followers
    """

    def test_get_followers(self, client, app):
        pass

    """
    Test get follower count
    """

    def test_get_follower_count(self, client, app):
        pass

    """
    Test get following count
    """

    def test_get_following_count(self, client, app):
        pass

    """
    Test local follow
    """

    def test_local_follow(self, client, app):
        pass

    """
    Test local unauthorized follow
    """

    def test_local_unauthorized_follow(self, client, app):
        pass

    """
    Test Non local follow
    """

    def test_non_local_follow(self, client, app):
        pass

    """
    Test Unauthorized non local follow
    """

    def test_non_local_unauthorized_follow(self, client, app):
        pass

    """
    Test remove local follower
    """

    def test_remove_local_follower(self, client, app):
        pass

    """
    Test remove non local follower
    """

    def test_remove_non_local_follower(self, client, app):
        pass

    """
    Test check is a follower
    """

    def test_check_is_follower(self, client, app):
        pass
