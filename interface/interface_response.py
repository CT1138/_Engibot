import random
from interface.interface_database import IF_Database, SQLCommands
from util import utils_string as uString


class IF_Response:
    def __init__(self):
        self.db = IF_Database()

    async def _get_strings_and_urls(self, key: str, param: str):
        await self.db.connect()
        responses = self.db.fetch(SQLCommands.GET_RESPONSES.value, (key,), all=True)
        urls = self.db.fetch(SQLCommands.GET_GIFS.value, (key,), all=True)

        response_strings = [row["content"] for row in responses] if responses else []
        url_strings = [row["content"] for row in urls] if urls else []

        MAX_LENGTH = 2000
        response_strings = uString.shorten_string(response_strings, MAX_LENGTH)
        url_strings = uString.shorten_string(url_strings, MAX_LENGTH)

        return response_strings, url_strings

    async def getArray(self, key="!placeholder", param="!placeholder"):
        return await self._get_strings_and_urls(key, param)

    async def getRandom(self, key="!placeholder", param="!placeholder"):
        response, urls = await self._get_strings_and_urls(key, param)

        s = random.choice(response) if response else ""
        u = random.choice(urls) if urls else ""
        return [s, u]

    async def getLast(self, key="!placeholder", param="!placeholder"):
        response, urls = await self._get_strings_and_urls(key, param)
        return [response[-1] if response else "", urls[-1] if urls else ""]

    async def get(self, key="!placeholder", param="!placeholder", index=0):
        response, urls = await self._get_strings_and_urls(key, param)
        s = response[index] if index < len(response) else ""
        u = urls[index] if index < len(urls) else ""
        return [s, u]

    async def add(self, key: str, phrase: str, gif=False):
        await self.db.connect()
        value = phrase.strip()
        if not value:
            return

        if gif:
            if not value.startswith("http"):
                raise ValueError("GIF value must be a valid URL starting with 'http'")
            value = value.strip()
            self.db.query(SQLCommands.INSERT_GIF.value, (key, value))
        else:
            self.db.query(SQLCommands.INSERT_RESPONSE.value, (key, value))
