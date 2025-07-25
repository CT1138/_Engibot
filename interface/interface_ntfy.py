import requests, os

# host|topic
URL = os.getenv("NTFY")
HOST, TOPIC = URL.split('|', 1)

class IF_NTFY:
    @staticmethod
    def post(msg: str):
        if not URL: return
        url = f"http://{HOST}/{TOPIC}"
        print(f"[NTFY] Posted \"{msg}\" to listeners")
        requests.post(url, data=msg)