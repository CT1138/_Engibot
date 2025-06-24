import random
from interface.interface_database import IF_Database, SQLCommands
from util import utils_string as uString


class IF_Response:
    def __init__(self):
        self.db = IF_Database()

    async def _get_strings_and_urls(self, key: str, param: str):
        await self.db.connect()
        result = self.db.fetch(SQLCommands.GET_RESPONSES.value, (key,), all=True)

        strings = []
        urls = []

        for row in result:
            content = row["content"].replace("{x}", param)
            if content.startswith("http"):
                urls.append(content)
            else:
                strings.append(content)

        MAX_LENGTH = 2000
        strings = uString.shorten_string(strings, MAX_LENGTH)
        urls = uString.shorten_string(urls, MAX_LENGTH)

        return strings, urls

    async def get_array(self, key="!placeholder", param="!placeholder"):
        return await self._get_strings_and_urls(key, param)

    async def get_random(self, key="!placeholder", param="!placeholder"):
        strings, urls = await self._get_strings_and_urls(key, param)

        s = random.choice(strings) if strings else ""
        u = random.choice(urls) if urls else ""
        return [s, u]

    async def get_last(self, key="!placeholder", param="!placeholder"):
        strings, urls = await self._get_strings_and_urls(key, param)
        return [strings[-1] if strings else "", urls[-1] if urls else ""]

    async def get(self, key="!placeholder", param="!placeholder", index=0):
        strings, urls = await self._get_strings_and_urls(key, param)
        s = strings[index] if index < len(strings) else ""
        u = urls[index] if index < len(urls) else ""
        return [s, u]

    async def add(self, key: str, is_response: bool, phrase: str):
        await self.db.connect()
        value = phrase.strip()
        if not value:
            return

        self.db.query(SQLCommands.INSERT_RESPONSE.value, (key, value))
