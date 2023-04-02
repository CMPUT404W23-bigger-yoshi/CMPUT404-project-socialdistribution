import pytest

from api import API_PATH
from api.admin.api_config import API_CONFIG
from api.app import create_app, db


class AuthActions(object):
    def __init__(self, client) -> None:
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(f"{API_PATH}/authors/login", json={"username": username, "password": password})

    def register(self, username="test", password="test"):
        return self._client.post(f"{API_PATH}/authors/register", json={"username": username, "password": password})

    def logout(self):
        return self._client.post(f"{API_PATH}/authors/logout")

    # For cross server API testing
    def register_node(self):
        pass


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app():
    app = create_app(testing_env=True)
    app.config.update({"TESTING": True})
    API_CONFIG.init_app(app)
    API_CONFIG.set_author_approval(False)

    yield app

    # Remove database/ Teardown
    with app.app_context():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def headers():
    return {"Authorization"}


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
