import os

from flask import request
from flask_basicauth import BasicAuth
from flask_login import current_user

from api.admin.api_config import API_CONFIG
from api.admin.inbound_connection import InboundConnection
from api.utils import Approval, is_admin_endpoint


class APIAuth(BasicAuth):

    """
    Overrides default behaviour of matching against only one
    username and password. Helps in registering multiple API
    callers.
    """

    def check_credentials(self, username, password):
        exist = InboundConnection.query.filter_by(username=username, password=password).first()
        return bool(exist and exist.approval == Approval.APPROVED)

    """
    Check the request for HTTP basic access authentication header and try
    to authenticate the user. Overrides and adds expectional routes.
    : returns: `True` if the user is authorized, or `False` otherwise.
    """

    def authenticate(self):
        auth = request.authorization
        path = request.full_path

        if current_user.is_authenticated:
            return True

        if not API_CONFIG.protect_api:
            return True

        # todo: this is somewhat obsolete
        if is_admin_endpoint(path) or request.host in [
            "localhost:5000",
            "127.0.0.1:5000",
            "bigger-yoshi.herokuapp.com",
        ]:
            # Basic authorization is not required for admin endpoints. Instead
            # the flask login will handle User permissions and only let the admin people in.
            return True

        return (auth and auth.type == "basic" and self.check_credentials(auth.username, auth.password)) or path in {
            "/?",
            "/nodes/register?",
            "/authors/register?",
            "/authors/login?",
            "/authors/authenticated_user_id?",
            "/authors/logout?",
        }
