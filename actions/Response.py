from util import utils_json as jReader 
from util import utils_string as uString
import random

# TODO: REPLACE JSON USAGE WITH A MYSQL SERVER

def getArray(asTerm="!placeholder", asParam="!placeholder"):
    RESPONSES = jReader.read("./__data/responses.json")[asTerm]
    STRINGS = [s.replace("{x}", asParam) for s in RESPONSES["_responses"]]
    URLS = RESPONSES["_urls"]

    # Shorten the responses in case
    MAX_LENGTH = 2000
    STRINGS = uString.shorten_string(STRINGS, MAX_LENGTH)
    URLS = uString.shorten_string(URLS, MAX_LENGTH)

    return [STRINGS, URLS]

def getRandom(asTerm="!placeholder", asParam="!placeholder"):
    STRINGS, URLS = getArray(asTerm, asParam)

    INDEX_S = -1
    INDEX_U = -1
    STRING = ""
    URL = ""

    if(len(STRINGS) > 0) : 
        INDEX_S = random.randrange(len(STRINGS))
        STRING = STRINGS[INDEX_S]
    if(len(URLS) > 0) : 
        INDEX_U = random.randrange(len(URLS))
        URL = URLS[INDEX_U]

    return [STRING, URL]

def getLast(asTerm="!placeholder", asParam="!placeholder"):
    STRINGS, URLS = getArray(asTerm, asParam)

    LAST_S = len(STRINGS) - 1
    LAST_U = len(URLS) - 1

    return [STRINGS[LAST_S], URLS[LAST_U]]

def get(asTerm="!placeholder", asParam="!placeholder", aiIndex=0):
    STRINGS, URLS = getArray(asTerm, asParam)
    
    return [STRINGS[aiIndex], URLS[aiIndex]]

def add(asTerm: str, abResponse:bool, asPhrase: str):
        if(abResponse) : 
            KEY = "_responses"
        else:
            KEY = "_urls"
        jReader.addList(
            file_path="./__data/responses.json",
            key_path=[asTerm, KEY],
            item=asPhrase
        )