import random
from sql.SQLCommands import SQLCommands
from interface.interface_database import IF_Database
from util import utils_string as uString
from enum import Enum

class ResultType(Enum):
    RESPONSE = "response"
    GIF = "gif"
    URL = "url"
    MEMORY = "memory"
    QUOTEBOOK = "quotebook"

class IF_Response:
    def __init__(self):
        self.db = IF_Database()

    async def getResult(self, key: str, result_type: ResultType):
        await self.db.connect()

        if result_type == ResultType.RESPONSE:
            data = self.db.fetch(SQLCommands.GET_RESPONSES.value, (key,), all=True)
            values = [row["content"] for row in data] if data else []
            return uString.shorten_string(values, 2000)

        elif result_type == ResultType.URL:
            data = self.db.fetch(SQLCommands.GET_GIFS.value, (key,), all=True)
            values = [row["content"] for row in data] if data else []
            return uString.shorten_string(values, 2000)

        elif result_type == ResultType.MEMORY:
            data = self.db.fetch(SQLCommands.GET_MEMORY.value, (key,), all=True)
            return [row["content"] for row in data] if data else []

        elif result_type == ResultType.QUOTEBOOK:
            data = self.db.fetch(SQLCommands.GET_QUOTEBOOK.value, (key,), all=True)
            return [row["content"] for row in data] if data else []

        else:
            raise ValueError(f"Unknown result type: {result_type}")

    async def getArray(self, key="!placeholder", result_type=ResultType.RESPONSE):
        return await self.getResult(key, result_type)

    async def getRandom(self, key="!placeholder", result_type=ResultType.RESPONSE):
        result = await self.getResult(key, result_type)
        s = random.choice(result) if result else ""
        return s

    async def getLast(self, key="!placeholder", result_type=ResultType.RESPONSE):
        result = await self.getResult(key, result_type)
        return result[-1] if result else ""

    async def get(self, key="!placeholder", index=0, result_type=ResultType.RESPONSE):
        result = await self.getResult(key, result_type)
        s = result[index] if 0 <= index < len(result) else ""
        return s

    async def add(self, key: str, phrase: str, result_type: ResultType):
        await self.db.connect()
        value = phrase.strip()
        if not value:
            return

        if result_type == ResultType.RESPONSE:
            self.db.query(SQLCommands.INSERT_RESPONSE.value, (key, value))

        elif result_type == ResultType.URL:
            if not value.startswith("http"):
                raise ValueError("URL must start with 'http'")
            self.db.query(SQLCommands.INSERT_GIF.value, (key, value))

        elif result_type == ResultType.MEMORY:
            self.db.query(SQLCommands.INSERT_MEMORY.value, (key, value))

        elif result_type == ResultType.QUOTEBOOK:
            self.db.query(SQLCommands.INSERT_QUOTEBOOK.value, (key, value))

        else:
            raise ValueError(f"Unsupported result type for add: {result_type}")
