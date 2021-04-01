import asyncio
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientSession
DEFAULT_API_ROOT = "https://api.flair.co"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/json",
}


class Auth:

    """Authenticate with API"""

    def __init__(self, credentials: dict, api_root=DEFAULT_API_ROOT):
        """TODO: successfully use credentials dict to authenticate and refresh
        with API.

        :credentials: TODO

        """
        self.credentials = credentials
        self.api_root = api_root

        async def create_url(self, path):
            return urljoin(self.api_root, path)

        async def oauth_token(self):
            params = dict(
                client_id=self.credentials["client_id"],
                client_secret=self.credentials["client_secret"],
                grant_type="client_credentials",
            )
            async with ClientSession as session:
                async with session.post(
                    self.create_url("/oauth/token"), params=params
                ) as resp:
                    self._token = resp.json().get("access_token") # For both of these - I'm not sure whether or not await is necessary
                    self._expires_in = resp.json().get("expires_in")
                    return resp.status

# class Control:
#
#     """Get status and control Flair products with API"""
#
#     def __init__(self, api=DEFAULT_API_ROOT):
#         """TODO
#
#         :api: TODO
#
#         """
#         api.__init__(self)
#
#         self._api = api
