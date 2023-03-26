import pytest

from api import API_ROOT
from api.user.author import model


class TestAuth:

    """
    Test registering mock user.
    """

    def test_register(self, client, app):
        response = client.post(f"{API_ROOT}/authors/register", json={"username": "test", "password": "test"})

        # TODO Should be a redirect ????
        print(response.data)
        assert response.status_code == 200
        # assert response.header["Location"] == "/auth/login"

        # Author should be created in database
        with app.app_context():
            assert model.Author.query.filter_by(username="test").first()

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
        response = client.post(f"{API_ROOT}/authors/register", json={"username": username, "password": password})

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

        response = client.post(f"{API_ROOT}/authors/logout")
        assert response.status_code == 200

        """
        Use the underneath if flask has to redirect.
        Add follow_redirects=True to post call above
        """
        # # Check that there was one redirect response.
        # assert len(response.history) == 1
        # # Check that the second request was to the ipage.
        # assert response.request.path == "/login"
