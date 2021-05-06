import asyncio
from urllib.parse import urljoin
from aiohttp import ClientResponse, ClientSession

DEFAULT_API_ROOT = "https://api.flair.co"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/json",
}


class Client:

    """Interact with Flair API"""

    def __init__(
        self, client_id=None, client_secret=None, api_root="https://api.flair.co"
    ):

        self.api_root = api_root
        self.client_id = client_id
        self.client_secret = client_secret

    # Create a url from the api root and added path
    async def create_url(self, path):
        return urljoin(self.api_root, path)

    # Retrieve OAuth token from API
    async def oauth_token(self, credentials: dict):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        async with ClientSession() as session:
            async with session.post(
                await self.create_url("/oauth/token"), params=params
            ) as resp:
                _json_body = await resp.json()

                return _json_body["credentials"]

    async def get_api_root_response(self):
        """Used to check wether or not the api is functional and get a list of
        links for the api, then put it in a dict."""
        async with ClientSession as session:
            async with session.get(self.create_url("/api/")) as resp:
                self.api_link_dict = resp.json()["links"]

    async def entity_url(self, entity_type, entity_id):
        """Create a path to the entity type and id if provided"""
        entity_path = self.api_link_dict[entity_type]["self"]
        if entity_id:
            resource_path = resource_path + "/" + str(entity_id)

    async def get(self, entity_name, entity_id):
        """Produce a dict of all entities of that kind, then store it under a dict key of the same name"""

        # Get a dict of paths and information to entity types
        await self.get_api_root_response()

        # Parameters to pass to aiohttp (the OAuth token we got with the oauth_token function)
        headers = {
            "Authorization": "Bearer " + str(await self.oauth_token(credentials))
        }
        #
        # The url to use
        # url = await self.create_url("/api/{entity}")
        url = await self.create_url(self.entity_url(entity_name))

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                # Dict with key that contain dict of all entity types as values
                entity_dict = {}

                # Nested dictionary magic
                entity_dict[entity_name] = await resp.json()
                self._entity_dict

    # Control entities visible to the API (E.g.: close & open vents)
    async def control(self, credentials, entity, action):
        DEFAULT_HEADERS["Authorization"] = (
            "Bearer " + await self.oauth_token(credentials)["credentials"]
        )
        headers = DEFAULT_HEADERS
        await self.get("structure", credentials)
