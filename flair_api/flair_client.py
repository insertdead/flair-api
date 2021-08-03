"""Interface with the Flair API"""
import asyncio
import json
from datetime import datetime
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientSession

DEFAULT_API_ROOT = "https://api.flair.co"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/json",
}


class Logging:
    """Enable logging and debugging levels"""

    def __init__(self, level):
        self.level = level

    def message(self, contents, urgency: int):
        if urgency == 0:
            print(f"LOG: {contents}")
        elif urgency == 1:
            print(f"WARN: {contents}")
        elif urgency == 2:
            print(f"ERROR: {contents}")
        else:
            print("Error printing message! Skipping")


class Utilities:
    """Utilities to avoid excessive boilerplate."""

    def __init__(self):
        pass

    # Create a url from the api root and added path
    async def create_url(self, path: str, api_root: str = DEFAULT_API_ROOT):
        """create_url.

        :param path:
        """
        return urljoin(api_root, path)

    async def get_api_root_response(self):
        """Get API root response"""
        async with ClientSession() as session:
            async with session.get(
                await self.create_url("/api/"), headers=DEFAULT_HEADERS
            ) as resp:
                self.api_link_dict = (await resp.json())["links"]
                return self.api_link_dict

    async def entity_url(self, entity_type: str, **kwargs: str):
        """Create an entity URL

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
    """Receive information from API"""

    def __init__(self, token: str = "", api_root=DEFAULT_API_ROOT):
        """Initialize"""
        self.token = token
        self.api_root = api_root

        self.api_link_dict = None

    # Retrieve OAuth token from API
    async def oauth_token(self, client_id, client_secret) -> ClientResponse:
        """Get OAuth token"""
        u = Utilities()
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
        return await ClientSession().post(
            await u.create_url("/oauth/token"), params=params
        )

    async def get(self, entity_type: str):
        """Retrieve information of a specific entity type from API

        :param entity_type:
        :type entity_type: str
        """
        u = Utilities()

        # Get a dict of paths and information to entity types
        # await u.get_api_root_response()

        # Parameters to pass to aiohttp (the OAuth token we got with the oauth_token function)
        headers = {"Authorization": "Bearer " + self.token}
        #
        # The url to use
        # url = await self.create_url("/api/{entity}")
        url = await u.create_url(await u.entity_url(entity_type))

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                # Dict with key that contain dict of all entity types as values
                Get.entity_dict = {}

                # Nested dictionary magic
                Get.entity_dict[entity_type] = await resp.json()


class Control:
    """Control entities"""

    def __init__(self, token: str = "", api_root=DEFAULT_API_ROOT):
        """Initialize"""

        self.token = token
        self.api_root = api_root

        self.api_link_dict = None

    # FIX: Not exactly sure what the issue is for this one, but I most likely have to use generators
    # async def sort_dicts(self, entity_type: str):
    #     g = Get(self.client_id, self.client_secret)
    #     await g.get(entity_type)
    #
    #     entity_dict = Get.entity_dict[entity_type]["data"]
    #     self.sorted_dict = {}
    #     for i in range(len(entity_dict)):
    #         name = entity_dict[i]["attributes"]["name"]
    #
    #         self.sorted_dict[entity_type][name] = entity_dict[i]
    #
    #     return self.sorted_dict

    async def control_entity(self, entity_type: str, id, body, headers=DEFAULT_HEADERS):
        """Control entities by sending a PATCH request to the API"""
        u = Utilities()
        path = await u.entity_url(entity_type, entity_id=id)
        url = await u.create_url(path)
        await u.get_api_root_response()
        async with ClientSession() as session:
            async with session.patch(url, headers=headers, data=body) as resp:
                Get.entity_dict[entity_type] = await resp.json()

    async def control(self, entity_type: str, body, **kwargs: str):
        u = Utilities()
        # g = Get(self.token, self.api_root)
        name = kwargs.get("name")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }
        """Control entities in the API"""
        # TODO: some funky dict stuff to allow use for all entity types
        # IDEA: maybe create some kind of way to sort through lists and put them
        # in a dict to name then to use later
        # entity_body = Get.entity_dict[entity_type]

        entity_body = {
            "data": {
                "type": entity_type,
                "attributes": body,
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

            # print(entity_dict[entity_num])
            id = entity_dict[entity_num]["id"]
            # print(id)
            await self.control_entity(
                entity_type,
                id,
                json.dumps(entity_body),
                headers,
            )


class Client:
    """Wrapper for all the previous classes"""

    def __init__(self, token: str):
        self.token = token

    async def get_entities(self, file="entities.json"):
        """Save the entity dict into a JSON file"""
        g = Get(self.token)
        u = Utilities()

        api_link_dict = await u.get_api_root_response()
        entity_dict = {"creation_time": datetime.now(), "data": {}}

        for index, key in enumerate(api_link_dict):
            await g.get(key)
            entity_dict["data"][key] = Get.entity_dict

        # Check if a file of the same name already exists
        try:
            open(file, "x")
        # Add a complain function/class to allow outputting warnings and errors to a log of some sort
        except:
            print("Warn: File already exists! Overwriting")

        output = open(file, "w")
        json.dump(entity_dict, output, indent=2)
        output.close()

    async def read_entities(self, file="entities.json") -> dict:
        """Import an entity class from a JSON file to avoid having to fetch from the API on every startup"""
        try:
            input = open(file, "r")
            entity_dict = json.load(input)
            input.close()
        except:
            # complain goes here as well
            print("Error: File does not exist! Skipping")
            entity_dict = {}

        return entity_dict

    # Wrapper methods here
    async def Control(self, entity_type, body, id):
        c = Control(self.token)

        await c.control_entity(entity_type, id, body)


# Might be useless - check later
# async def make_client(client_id: str, client_secret: str, api_root=DEFAULT_API_ROOT):
#     """Initialize variables for classes"""
#     resp = await Get().oauth_token(client_id, client_secret)
#     json = await resp.json()
#     token = json["access_token"]
