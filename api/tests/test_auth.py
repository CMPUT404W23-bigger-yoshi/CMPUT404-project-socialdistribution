import pytest
from flask import session
from flask_login import current_user

from api import API_PATH
from api.tests.resources.mock_authors import *
from api.user.author.model import Author


class TestAuthUnit:

    """
    Test registering mock user.
    """

    def test_register(self, client, app):
        response = client.post(f"{API_PATH}/authors/register", json={"username": "test", "password": "test"})

        assert response.status_code == 200

        with app.app_context():
            assert Author.query.filter_by(username="test").first()

    """
    Test registering with invalid credentials.
    """

    @pytest.mark.parametrize(
        ("username", "password", "response_code"),
        (
            ("", "", 400),
            ("xyz", "", 400),
        ),
    )
    def test_register_invalid_input(self, client, username, password, response_code):
        response = client.post(f"{API_PATH}/authors/register", json={"username": username, "password": password})

        assert response.status_code == response_code

    """
    Test registering with duplicate username
    """

    def test_reregister(self, client, auth):
        auth.register()

        second_response = auth.register()
        assert second_response.status_code == 409

    """
    Test successful logout
    """

    def test_logout(self, client, auth):
        # Register and Login first
        auth.register()
        auth.login()

        response = client.post(f"{API_PATH}/authors/logout")
        assert response.status_code == 200


"""
API tests are for matching expected response from server
"""


class TestAuthorAPI:

    """
    Test get all authors
    """

    def test_get_all_authors(self, client, auth):
        cred1 = {"username": mock_author1["displayName"], "password": "123"}
        cred2 = {"username": mock_author2["displayName"], "password": "123"}

        register = client.post(f"{API_PATH}/authors/register", json=cred1)
        assert register.status_code == 200

        register = client.post(f"{API_PATH}/authors/register", json=cred2)
        assert register.status_code == 200

        response = client.get(f"{API_PATH}/authors", follow_redirects=True)
        assert response.status_code == 200
        data = response.json

        # Check keys
        type = data.get("type", None)
        assert type is not None

        items = data.get("items", None)
        assert items is not None

        author_list = data.get("items")
        usernames = set()
        for author in author_list:
            assert set(mock_author1.keys()) == set(author.keys())
            usernames.add(author["displayName"])

        assert mock_author1["displayName"] in usernames and mock_author2["displayName"] in usernames

    """
    Test get single author
    """

    def test_get_single_author(self, client, auth, app):
        auth.register()

        with app.app_context():
            test_author = Author.query.filter_by(username="test").first()
        assert test_author

        id = test_author.id

        response = client.get(f"{API_PATH}/authors/{id}", follow_redirects=True)
        assert response.status_code == 200

        author = response.json
        assert set(mock_author1.keys()) == set(author.keys())

        url_id = author["id"]
        data_id = url_id.split("/")[-1]
        assert data_id == id

    """
    Test updating author
    """

    def test_update_author(self, client, auth, app):
        auth.register()

        with app.app_context():
            test_author = Author.query.filter_by(username="test").first()
        assert test_author

        id = test_author.id
        old_data = test_author.getJSON()
        new_data = old_data.copy()

        new_data["displayName"] = "modified"

        # Check updated author username
        response = client.post(f"{API_PATH}/authors/{id}", json=new_data, follow_redirects=True)
        assert response.status_code == 200
        data = response.json

        new_username = data.get("displayName", None)
        assert new_username and new_username == "modified"

    """
    Test existing username
    """

    def test_existing_username(self, client, app, auth):
        auth.register()

        with app.app_context():
            test_author = Author.query.filter_by(username="test").first()
        assert test_author

        id = test_author.id
        old_data = test_author.getJSON()
        new_data = old_data.copy()

        new_data["displayName"] = "modified"

        # Check updated author username
        response = client.post(f"{API_PATH}/authors/{id}", json=new_data, follow_redirects=True)
        assert response.status_code == 200
        data = response.json

        new_username = data.get("displayName", None)
        assert new_username and new_username == "modified"

        # Check changing username to an existing one
        auth.register()  # new test user

        with app.app_context():
            test_author = Author.query.filter_by(username="test").first()
        assert test_author

        id = test_author.id
        old_data = test_author.getJSON()
        new_data = old_data.copy()

        new_data["displayName"] = "modified"

        response = client.post(f"{API_PATH}/authors/{id}", json=new_data, follow_redirects=True)
        assert response.status_code == 409  # User with username "modified" was just updated

    """
    Test if logged in user can only update their own profile
    """

    def test_own_update_only(self, client, auth, app):
        with client:
            creds = {"username": "user2", "password": "123"}
            client.post(f"{API_PATH}/authors/register", json=creds, follow_redirects=True)

            with app.app_context():
                user2 = Author.query.filter_by(username=creds["username"]).first()
            json = user2.getJSON()
            json["username"] = "Changed"
            auth.register()
            auth.login()
            client.post(
                f"{API_PATH}/authors/login", json={"username": "test", "password": "test"}, follow_redirects=True
            )
            response = client.post(f"{API_PATH}/authors/{user2.id}", json=json, follow_redirects=True)
            assert response.status_code == 401
