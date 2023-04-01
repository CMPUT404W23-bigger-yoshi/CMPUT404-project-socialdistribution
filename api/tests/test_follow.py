import urllib.parse

import pytest
from flask_login import current_user

from api import API_ROOT
from api.tests.resources.mock_authors import foreign_mock_author, mock_author1, mock_author2
from api.tests.resources.mock_follow import mock_follow_request
from api.user.author.model import Author
from api.user.followers.model import LocalFollower, NonLocalFollower


class TestFollow:
    MockFollowed: dict = None
    MockFollower: dict = None
    MockForeignFollower: dict = foreign_mock_author
    MockFollowRequest = None
    MockForeignRequest = None

    """
    Needed in tests below
    """

    @pytest.fixture(scope="function", autouse=True)
    def register_mock_authors(self, client, app):
        client.post(f"{API_ROOT}/authors/register", json={"username": mock_author1["displayName"], "password": "test"})
        client.post(f"{API_ROOT}/authors/register", json={"username": mock_author2["displayName"], "password": "test"})
        with app.app_context():
            self.MockFollowed = Author.query.filter_by(username=mock_author1["displayName"]).first().getJSON()
            self.MockFollower = Author.query.filter_by(username=mock_author2["displayName"]).first().getJSON()
            self.MockFollowRequest = {
                "type": "Follow",
                "summary": f"{self.MockFollower['displayName']} wants to follow {self.MockFollowed['displayName']}",
                "actor": self.MockFollower,
                "object": self.MockFollowed,
            }
            self.MockForeignRequest = {
                "type": "Follow",
                "summary": f"{self.MockForeignFollower['displayName']} wants to follow {self.MockFollowed['displayName']}",
                "actor": self.MockForeignFollower,
                "object": self.MockFollowed,
            }

    """
    This is tested independently as well. Will fail if test_local_follow
    fails or test_nonlocal follow fails.
    Logs in the follower before sending request.
    """

    def send_follow(self, client, auth, local=True):
        followed = self.MockFollowed["id"].split("/")[-1]
        if local:
            follower = self.MockFollower["id"].split("/")[-1]
            login_cred = {"username": self.MockFollower["displayName"], "password": "test"}
            auth.login(**login_cred)
            client.post(f"{API_ROOT}/authors/{followed}/inbox", json=self.MockFollowRequest, follow_redirects=True)
            auth.logout()
        else:
            follower = urllib.parse.quote(self.MockForeignFollower["id"], safe="")
            client.post(f"{API_ROOT}/authors/{followed}/inbox", json=self.MockForeignRequest, follow_redirects=True)

        return (followed, follower)

    """
    This is tested independently as well
    """

    def approve_follow(self, client, auth, local=True):
        creds = {"username": self.MockFollowed["displayName"], "password": "test"}
        auth.login(**creds)
        followed_id = self.MockFollowed["id"].split("/")[-1]
        if local:
            follower_id = self.MockFollower["id"]
        else:
            follower_id = self.MockForeignFollower["id"]
        follower_id = urllib.parse.quote(follower_id, safe="")
        client.put(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
        auth.logout()

    """
    Test get all followers
    """

    def test_get_followers(self, client, auth, app):
        # Can login anyone here just to bypass basic auth
        with client:
            auth.register()
            followed_id, follower_id = self.send_follow(client, auth)
            self.approve_follow(client, auth)
            auth.login()
            response = client.get(f"{API_ROOT}/authors/{followed_id}/followers", follow_redirects=True)
        assert response.status_code == 200

        data = response.json
        type = data.get("type", None)
        items = data.get("items", None)

        assert type is not None and items is not None
        assert len(items) > 0
        assert type == "followers"

        assert set(self.MockFollowed.keys()) == set(items[0].keys())

        followers = [item["displayName"] for item in items]
        assert self.MockFollower["displayName"] in followers

    """
    Test get follower count
    """

    def test_get_follower_count(self, client, auth, app):
        with client:
            auth.register()
            followed_id, follower_id = self.send_follow(client, auth)
            self.approve_follow(client, auth)
            auth.login()
            with app.app_context():
                print(LocalFollower.query.all())
            response = client.get(f"{API_ROOT}/authors/{followed_id}/followers/count", follow_redirects=True)
        assert response.status_code == 200
        assert response.json["count"] == 1

    """
    Test local follow
    """

    def test_local_follow(self, client, auth, app):
        followed_id = self.MockFollowed["id"].split("/")[-1]
        followed_url = self.MockFollowed["url"]
        follower_id = self.MockFollower["id"].split("/")[-1]
        follower_url = self.MockFollower["url"]
        login_cred = {"username": follower_id, "password": "test"}
        with client:
            auth.login(**login_cred)
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockFollowRequest, follow_redirects=True
            )
            auth.logout()
        assert response.status_code == 201

        with app.app_context():
            request_sent = LocalFollower.query.filter_by(followed_url=followed_url, follower_url=follower_url).first()
        assert request_sent

    """
    Test Local follow twice
    """

    def test_local_follow_twice(self, client, auth):
        followed_id = self.MockFollowed["id"].split("/")[-1]
        followed_url = self.MockFollowed["url"]
        follower_id = self.MockFollower["id"].split("/")[-1]
        follower_url = self.MockFollower["url"]
        login_cred = {"username": self.MockFollower["displayName"], "password": "test"}
        with client:
            auth.login(**login_cred)
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockFollowRequest, follow_redirects=True
            )
            auth.logout()
        assert response.status_code == 200

        # Send again
        with client:
            auth.login(**login_cred)
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockFollowRequest, follow_redirects=True
            )
            auth.logout()
        assert response.status_code == 409  # Conflict

    """
    Test local unauthorized follow
    """

    def test_local_unauthorized_follow(self, client, auth):
        followed_id = self.MockFollowed["id"].split("/")[-1]
        followed_url = self.MockFollowed["url"]
        follower_id = self.MockFollower["id"].split("/")[-1]
        follower_url = self.MockFollower["url"]

        # Unauthorized request
        with client:
            auth.logout()
            assert not current_user.is_authenticated
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockFollowRequest, follow_redirects=True
            )
        assert response.status_code == 401

    """
    Test local invalid follow
    """

    def test_local_invalid_follow(self, client, auth):
        # No object
        followed_id = self.MockFollowed["id"].split("/")[-1]
        followed_url = self.MockFollowed["url"]
        follower_id = self.MockFollower["id"].split("/")[-1]
        follower_url = self.MockFollower["url"]
        login_creds = {"username": self.MockFollower["displayName"], "password": "test"}
        with client:
            auth.login(**login_creds)
            response = client.post(f"{API_ROOT}/authors/{followed_id}/inbox", follow_redirects=True)
        assert response.status_code == 400

    """
    Test Non local follow
    """

    def test_non_local_follow(self, client, auth, app):
        # login as anyone to bypass basic auth
        followed_id = self.MockFollowed["id"].split("/")[-1]
        followed_url = self.MockFollowed["url"]
        follower_url = self.MockForeignFollower["url"]
        with client:
            auth.login()
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockForeignRequest, follow_redirects=True
            )
        assert response.status_code == 201

        with app.app_context():
            request_sent = NonLocalFollower.query.filter_by(
                followed_url=followed_url, follower_url=follower_url
            ).first()
            assert NonLocalFollower.query.count() == 1
        assert request_sent

    """
    Test non local follow twice
    """

    def test_non_local_follow_twice(self, auth, client):
        followed_id = self.MockFollowed["id"].split("/")[-1]
        with client:
            auth.login()
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockForeignRequest, follow_redirects=True
            )
            auth.logout()
        assert response.status_code == 201

        with client:
            auth.login()
            response = client.post(
                f"{API_ROOT}/authors/{followed_id}/inbox", json=self.MockForeignRequest, follow_redirects=True
            )
            auth.logout()
        assert response.status_code == 409

    """
    Test non local follow invalid
    """

    def test_non_local_follow_invalid(self, client, auth):
        # Without object
        # login as anyone to bypass basic auth
        followed_id = self.MockFollowed["id"].split("/")[-1]
        with client:
            auth.login()
            response = client.post(f"{API_ROOT}/authors/{followed_id}/inbox", follow_redirects=True)
        assert response.status_code == 400

    """
    Test Unauthorized non local follow
    """

    def test_non_local_unauthorized_follow(self, client, auth):
        followed_id = self.MockFollowed["id"].split("/")[-1]
        with client:
            auth.logout()
            assert not current_user.is_authenticated
            response = client.post(f"{API_ROOT}/authors/{followed_id}/inbox", follow_redirects=True)
        assert response.status_code == 401

    """
    Test remove local follower
    """

    def test_remove_local_follower(self, client, app, auth):
        with client:
            self.send_follow(client, auth)
            self.approve_follow(client, auth)

            with app.app_context():
                # The follow must be made and approved
                follow_made = LocalFollower.query.all()
                assert follow_made

            followed_id = self.MockFollowed["id"].split("/")[-1]
            follower_id = self.MockFollower["id"].split("/")[-1]
            login_creds = {"username": self.MockFollowed["displayName"], "password": "test"}
            auth.login(**login_creds)
            response = client.delete(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}")
        assert response.status_code == 200

        with app.app_context():
            follows = LocalFollower.query.count()
        assert follows == 0

    """
    Test remove non local follower
    """

    def test_remove_non_local_follower(self, client, auth, app):
        with client:
            self.send_follow(client, auth, local=False)
            self.approve_follow(client, auth, local=False)

            with app.app_context():
                # The follow must be made and approved
                follow_made = NonLocalFollower.query.all()
                assert follow_made

            followed_id = self.MockFollowed["id"].split("/")[-1]
            follower_id = urllib.parse.quote(self.MockForeignFollower["id"], safe="")
            login_creds = {"username": self.MockFollowed["displayName"], "password": "test"}
            auth.login(**login_creds)
            response = client.delete(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}")
        assert response.status_code == 200

        with app.app_context():
            follows = NonLocalFollower.query.count()
        assert follows == 0

    """
    Test check is a follower
    """

    def test_check_is_follower(self, client, auth):
        # Bypass basic auth
        with client:
            self.send_follow(client, auth, local=False)
            self.approve_follow(client, auth, local=False)

            followed_id = self.MockFollowed["id"].split("/")[-1]
            follower_id = urllib.parse.quote(self.MockForeignFollower["id"], safe="")
            auth.register()
            auth.login()
            response = client.get(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            auth.logout()
        assert response.status_code == 200
        found = response.json["found"]
        assert found == True

    """
    Test check cannot follow self
    """

    def test_check_self_follow(self, client, auth):
        with client:
            followed_id = self.MockFollowed["id"].split("/")[-1]
            follower_id = urllib.parse.quote(self.MockFollowed["id"], safe="")
            login_creds = {"username": self.MockFollowed["displayName"], "password": "test"}

            # Try to follow self
            req_obj = self.MockFollowRequest.copy()
            req_obj["object"] = self.MockFollowed

            auth.login(**login_creds)
            response = client.post(f"{API_ROOT}/authors/{followed_id}/inbox", json=req_obj, follow_redirects=True)
            auth.logout()

        assert response.status_code == 400

    """
    Test approve local follow request
    """

    def test_approve_follow_request(self, client, auth):
        self.send_follow(client, auth)
        # not approved yet
        followed_id = self.MockFollowed["id"].split("/")[-1]
        follower_id = urllib.parse.quote(self.MockFollower["id"], safe="")
        login_creds = {"username": self.MockFollowed["displayName"], "password": "test"}
        with client:
            auth.login(**login_creds)
            response1 = client.put(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            response2 = client.get(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            auth.logout()
            assert response1.status_code == 200
            assert response2 == 200
            assert response2.json["found"] == True

    """
    Test approve non local follow request
    """

    def test_approve_non_follow_request(self, client, auth):
        self.send_follow(client, auth, local=False)
        # not approved yet
        followed_id = self.MockFollowed["id"].split("/")[-1]
        follower_id = urllib.parse.quote(self.MockForeignFollower["id"], safe="")
        login_creds = {"username": self.MockFollowed["displayName"], "password": "test"}
        with client:
            auth.login(**login_creds)
            response1 = client.put(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            response2 = client.get(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            auth.logout()
            assert response1.status_code == 200
            assert response2 == 200
            assert response2.json["found"] == True

    """
    Test Unauthorized approval (Logged in as different user)
    """

    def test_unauthorized_approval(self, client, auth):
        self.send_follow(client, auth)
        # not approved yet
        followed_id = self.MockFollowed["id"].split("/")[-1]
        follower_id = urllib.parse.quote(self.MockFollower["id"], safe="")
        with client:
            response1 = client.put(f"{API_ROOT}/authors/{followed_id}/followers/{follower_id}", follow_redirects=True)
            assert response1.status_code == 401
