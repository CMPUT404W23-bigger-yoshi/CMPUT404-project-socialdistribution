"""API configuration."""
import logging
from dataclasses import dataclass
from typing import Any

from api import db

logger = logging.getLogger(__name__)


@dataclass
class _APIConfigVals(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    node_limit: int = db.Column(db.Integer, default=100)
    protect_api: bool = db.Column(db.Boolean, default=False)
    restrict_signups: bool = db.Column(db.Boolean, default=False)


class APIConfigLazyLoader:
    """
    - we need the app context to access the database
    - we need the API config for values for various parts of the app on startup
    - we can't import app context here because of trick circular imports
    solution:
    - return this instance immediately, then after is initialized, actually go and populate these values.
    """

    def __init__(self):
        self.node_limit = ...
        self.restrict_signups = ...
        self.protect_api = ...
        self.config_row = None
        self.app = None

    def init_app(self, app):
        self.app = app
        with app.app_context():
            # app must be initialized before this is called!
            self.config_row = _APIConfigVals.query.first()
            if self.config_row is None:
                logger.info("creating config row for the first time")
                self.config_row = _APIConfigVals()
                db.session.add(self.config_row)
                db.session.commit()
            else:
                logger.info("retrieved config row successfully")
            # I hope we don't have too many more of these. it's a bit much :/
            self.protect_api = self.config_row.protect_api
            self.restrict_signups = self.config_row.restrict_signups
            self.node_limit = self.config_row.node_limit

    def _set_attr(self, key: str, val: Any):
        logger.info(f"setting config: {key}={val}")
        # this is the value that others fetch from us
        setattr(self, key, val)
        # this is the value that gets saved to db. ugly i know
        setattr(self.config_row, key, val)
        with self.app.app_context():
            db.session.commit()

    def set_node_limit(self, limit: int):
        return self._set_attr("node_limit", limit)

    def set_author_approval(self, val: bool):
        return self._set_attr("restrict_signups", val)

    def set_api_protection(self, val: bool):
        return self._set_attr("protect_api", val)


API_CONFIG = APIConfigLazyLoader()
