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

    def __init__(self, api_root=DEFAULT_API_ROOT):

        self.api_root = api_root

    # Create a url from the api root and added path
    async def create_url(self, path):
        return urljoin(self.api_root, path)

    # Retrieve OAuth token from API
    async def oauth_token(self, credentials: dict):
        params = {
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "grant_type": "client_credentials",
        }
        async with ClientSession() as session:
            async with session.post(
                await self.create_url("/oauth/token"), params=params
            ) as resp:
                _json_body = await resp.json()

                return _json_body["access_token"]

    async def get(self, entity_name, credentials):

        """Produce a dict of all entities of that kind, then store it under a dict key of the same name"""

        # Parameters to pass to aiohttp (the OAuth token we got with the oauth_token function)
        headers = {
            "Authorization": "Bearer " + str(await self.oauth_token(credentials))
        }
        # Dict with key that contain dict of all entity types as values
        entity_dict = {}
        # The url to use
        url = await self.create_url("/api/{entity}")

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                # Nested dictionary magic
                entity_dict[entity_name] = await resp.json()
                print(str(entity_dict))
        # Broken i think
        # """IDs of entities, to use with control()"""
        # temp1 = await self.oauth_token(credentials)
        # params = dict(Authorization="Bearer " + str(temp1))
        # entity_dict = dict()

        # async def get_entity(entity: str):
        #     """Make code more readable, and shorten length of code"""

        #     if entity_name == entity:
        #         async with ClientSession as session:
        #             async with session.get(
        #                 await self.create_url("/api/{entity}"), params=params
        #             ) as resp:
        #                 # Some nested dictionary magic
        #                 entity_dict[entity] = resp.json()
        #                 return entity_dict

        #                 # self.entity_dict[str(entity)] = await resp.json()
        #                 # return await resp.status

        #     else:
        #         return "Error: Please use a proper entity name"

        # # try:
        # # Now to just await the results...
        # await get_entity(entity=entity_name)

        # # except Exception:
        # #     print("Oops! something happened")
        # #     print("Error Code: TODO: make an error system to aid with troubleshooting")

    # Control entities visible to the API (E.g.: close & open vents)
    async def control(self, entity, action):
        DEFAULT_HEADERS["Authorization"] = "Bearer " + self._json_body["access_token"]
        headers = DEFAULT_HEADERS

        url = self.create_url("/api/{entity}")
