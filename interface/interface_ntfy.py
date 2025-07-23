from interface.interface_json import IF_JSON
import requests
TOKENS = IF_JSON("./__data/tokens.json").json

class IF_NTFY:
    def post(msg: str):
        host = TOKENS["NTFY"]["host"]
        topic = TOKENS["NTFY"]["topic"]
        url = f"http://{host}/{topic}"
        print(f"[NTFY] Posted \"msg\" to listeners")
        requests.post(url, data=msg)