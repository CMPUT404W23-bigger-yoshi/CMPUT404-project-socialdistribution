from flask import request
from flask_basicauth import BasicAuth

from api.admin.APIConfig import APIConfig
from api.admin.model import Connection
from api.utils import Approval, is_admin_endpoint


class APIAuth(BasicAuth):

    """
    Overrides default behaviour of matching against only one
    username and password. Helps in registering multiple API
    callers.
    """

    def check_credentials(self, username, password):
        exist = Connection.query.filter_by(username=username, password=password).first()

        return exist and exist.approval == Approval.APPROVED

    """
    Custom function to check if the credentials are the owner's credentials for special endpoints.
    """

    def check_admin_credentials(self, username, password):
        return username == APIConfig.SELF_USERNAME and password == APIConfig.SELF_PASSWORD

    """
    Check the request for HTTP basic access authentication header and try
    to authenticate the user. Overrides and adds expectional routes.
    : returns: `True` if the user is authorized, or `False` otherwise.
    """

    def authenticate(self):
        auth = request.authorization
        path = request.full_path

        if is_admin_endpoint(path):
            ret = auth and auth.type == "basic" and self.check_admin_credentials(auth.username, auth.password)
        else:
            ret = (
                not APIConfig.is_API_protected
                or (auth and auth.type == "basic" and self.check_credentials(auth.username, auth.password))
                or path
                in {
                    "/nodes/register?",
                    "/authors/register?",
                    "/authors/login?",
                    "/authors/authenticated_user_id?",
                    "/authors/logout?",
                }
            )
        return ret
