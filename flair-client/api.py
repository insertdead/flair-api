"""Interface with the Flair API"""
from urllib.parse import urljoin
import json

from aiohttp import ClientSession

DEFAULT_API_ROOT = "https://api.flair.co"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/json",
}


class Utilities:
    """Utilities."""

    def __init__(self, api_root=DEFAULT_API_ROOT):
        """__init__.

        :param api_root:
        """
        self.api_root = api_root

    # Create a url from the api root and added path
    async def create_url(self, path: str):
        """create_url.

        :param path:
        """
        return urljoin(self.api_root, path)

    async def get_api_root_response(self):
        """get_api_root_response."""
        async with ClientSession() as session:
            async with session.get(
                await self.create_url("/api/"), headers=DEFAULT_HEADERS
            ) as resp:
                self.api_link_dict = (await resp.json())["links"]

    async def entity_url(self, entity_type: str, **kwargs: str):
        """entity_url.

        :param entity_type:
        :param kwargs:
        """
        await self.get_api_root_response()
        entity_id = kwargs.get("entity_id")
        entity_path = self.api_link_dict[entity_type]["self"]
        if entity_id:
            entity_path = entity_path + "/" + str(entity_id)

        return entity_path


class Get:
    """Get."""

    def __init__(self, client_id=None, client_secret=None, api_root=DEFAULT_API_ROOT):
        """__init__.

        :param client_id:
        :param client_secret:
        :param api_root:
        """

        self.api_root = api_root
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_link_dict = None

    # Retrieve OAuth token from API
    async def oauth_token(self):
        """Get OAuth token"""
        u = Utilities()
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        async with ClientSession() as session:
            async with session.post(
                await u.create_url("/oauth/token"), params=params
            ) as resp:
                _json_body = await resp.json()

                return _json_body["access_token"]

    async def get(self, entity_name: str):
        """get.

        :param entity_name:
        :type entity_name: str
        """
        u = Utilities()

        # Get a dict of paths and information to entity types
        # await u.get_api_root_response()

        # Parameters to pass to aiohttp (the OAuth token we got with the oauth_token function)
        headers = {"Authorization": "Bearer " + str(await self.oauth_token())}
        #
        # The url to use
        # url = await self.create_url("/api/{entity}")
        url = await u.create_url(await u.entity_url(entity_name))

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                # Dict with key that contain dict of all entity types as values
                Get.entity_dict = {}

                # Nested dictionary magic
                Get.entity_dict[entity_name] = await resp.json()

    async def check_auto_mode(self):
        """check_auto_mode."""
        await self.get("structures")
        return (
            True if self.entity_dict["structures"]["data"]["mode"] == "auto" else False
        )


class Control:
    """Control entities."""

    def __init__(self, client_id=None, client_secret=None, api_root=DEFAULT_API_ROOT):
        """__init__.

        :param client_id:
        :param client_secret:
        :param api_root:
        """

        self.api_root = api_root
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_link_dict = None

    async def control_entity(
        self, entity_type: str, id, body, headers=DEFAULT_HEADERS, **kwargs
    ):
        u = Utilities()
        path = await u.entity_url(entity_type, entity_id=id)
        url = await u.create_url(path)
        await u.get_api_root_response()
        async with ClientSession() as session:
            async with session.patch(url, headers=headers, data=body) as resp:
                Get.entity_dict[entity_type] = await resp.json()

    async def control(self, entity_type: str, body, **kwargs: str):
        u = Utilities()
        g = Get(self.client_id, self.client_secret)
        name = kwargs.get("name")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + await g.oauth_token(),
        }
        """Control vents. It is highly recommended to fill out the reason variable
        :param percent_open:
        :type percent_open: int
        :param reason:
        :param kwargs:
        :type kwargs: str
        """
        # TODO: some funky dict stuff to allow use for all entity types
        # IDEA: maybe create some kind of way to sort through lists and put them
        # in a dict to name then to use later
        entity_body = Get.entity_dict[entity_type]

        entity_body = {
            "data": {
                body,
            }
        }
        # If id is supplied, use that instead of name
        if "id" in kwargs:
            await self.control_entity(
                entity_type,
                kwargs.get("id"),
                json.dumps(entity_body),
                headers,
            )

        else:
            # Get id from supplied name; If user error occurs, raise ValueError
            await u.entity_url(entity_type)
            entity_dict = Get.entity_dict[entity_type]["data"]
            # Not sure how this works as I 'borrowed' it from SO
            entity_num = next(
                (
                    i
                    for i, item in enumerate(entity_dict)
                    if item["attributes"]["name"] == name
                ),
                None,
            )

            if entity_num == None:
                raise ValueError("Name of vent does not match with any in the API!")

            id = entity_dict[entity_num]["data"]["id"]
            await self.control_entity(entity_type, id, body, headers)


class Client:
    """Interact with Flair API"""

    def __init__(self, client_id=None, client_secret=None, api_root=DEFAULT_API_ROOT):
        """__init__.

        :param client_id:
        :param client_secret:
        :param api_root:
        """

        self.api_root = api_root
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_link_dict = None

    # Control entities visible to the API (E.g.: close & open vents)
    async def control(self, credentials, entity, action):
        """control.

        :param credentials:
        :param entity:
        :param action:
        """
        u = Utilities()
        g = Get()

        DEFAULT_HEADERS["Authorization"] = "Bearer " + await g.oauth_token()
        headers = DEFAULT_HEADERS
        await g.get("structures")

        auto_mode = await g.check_auto_mode()

        # If auto mode is detected, disable some functions/issue a warning as
        # they will not be useful.
        if auto_mode == 1:
            pass
