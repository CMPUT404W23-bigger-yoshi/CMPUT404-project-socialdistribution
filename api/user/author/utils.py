import asyncio
import itertools
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import httpx
import requests

from api.admin.utils import auth_header_for_url

logger = logging.getLogger(__name__)


async def retrieve_authors_from_endpoints(endpoints: List[str]):
    async with httpx.AsyncClient() as client:
        tasks = [
            *map(
                lambda endpoint: asyncio.ensure_future(retrieve_authors_from_single_endpoint(client, endpoint)),
                endpoints,
            )
        ]

        return [*itertools.chain(*(await asyncio.gather(*tasks)))]


async def retrieve_authors_from_single_endpoint(client: httpx.AsyncClient, endpoint: str) -> List[str]:
    endpoint_headers = auth_header_for_url(endpoint)
    logger.debug(f"/authors request: {endpoint=} {endpoint_headers=}")
    try:
        resp = await cache_request.get(
            client, endpoint, headers=endpoint_headers, follow_redirects=True, timeout=2, params={"size": 100}
        )
        if resp.status_code != 200:
            logger.warning(f"non-200 resp from {endpoint=}: {resp.status_code=}")
    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as e:
        logger.error(f"failed to get {endpoint=} {e=}")
        return []
    except Exception as e:
        logger.exception(f"failed to get {endpoint=}")
        return []

    try:
        parsed = resp.json()
    except Exception as e:
        logger.warning(f"failed to decode resp: {resp.content.decode()=} {e}")
        return []

    return parsed.get("items", [])


@dataclass
class CachedResponse:
    time: datetime
    resp: Any


class _RequestCacher:
    """
    requests doesn't cache responses, let's roll our own
    ignore cache control headers
    embrace client knowing what's best for it
    (in reality, lots of endpoints don't have cache control implemented, and we hammer endpoints)
    """

    def __init__(self, cache_time_s: float):
        self.responses: Dict[Tuple, CachedResponse] = {}
        self.cache_timedelta = timedelta(seconds=cache_time_s)

    async def _retrieve_from_cache_or_make_request(self, key):
        refresh = True
        if key in self.responses.keys():
            cached_resp = self.responses[key]
            # if now is past the amount of time we intended to cache for...
            if datetime.now() < (cached_resp.time + self.cache_timedelta):
                # no need to re-make the request, it's within the caching interval
                refresh = False

        if refresh:
            # wow this is really uglier than i intended it to be. too late to go back idc
            function, args, kwargs = key
            cached_resp = self.responses[key] = CachedResponse(
                datetime.now(), await function(*args, **json.loads(kwargs))
            )

        return cached_resp.resp

    async def get(self, client: httpx.AsyncClient, *args, **kwargs):
        # ok, I'm sorry. I never realized that this way of implementing caching would have been so cursed
        # I never would have done it
        key = (client.get, tuple(args), json.dumps(kwargs, sort_keys=True))
        return await self._retrieve_from_cache_or_make_request(key)


cache_request = _RequestCacher(cache_time_s=3)
