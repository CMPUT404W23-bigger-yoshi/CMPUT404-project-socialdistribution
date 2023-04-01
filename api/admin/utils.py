import logging
from typing import Dict

from api.admin.outbound_connection import OutboundConnection

logger = logging.getLogger(__name__)


def auth_header_for_url(url: str) -> Dict[str, str]:
    configured_endpoints = set()
    for connection in OutboundConnection.query.all():
        configured_endpoints.add(connection.endpoint)
        if connection.matches_url(url):
            return connection.auth_header_dict
    logger.error(f"Failed to match {url=} with {configured_endpoints=}")
    return {}  # is it bad to fail silently? yes. i know. I'm well aware.
