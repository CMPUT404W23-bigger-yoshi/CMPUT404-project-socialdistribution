import base64

from flask import request
from flask_basicauth import BasicAuth

from api.admin.model import Connection


class APIAuth(BasicAuth):

    """
    Overrides default behaviour of matching against only one
    username and password. Helps in registering multiple API
    callers.
    """

    def check_credentials(self, username, password):
        exist = Connection.query.filter_by(username=username, password=password).first()

        if exist:
            return True
        return False

    """
    Check the request for HTTP basic access authentication header and try
    to authenticate the user. Overrides and adds expectional routes.
    :returns: `True` if the user is authorized, or `False` otherwise.
    """

    def authenticate(self):
        auth = request.authorization
        path = request.full_path
        return (auth and auth.type == "basic" and self.check_credentials(auth.username, auth.password)) or path in {
            "/nodes/register?"
        }
