import requests, os


class IF_NTFY:
    @staticmethod
    def post(msg: str):
        # host|topic
        URL = os.getenv("NTFY")
        if not URL: return
        HOST, TOPIC = URL.split('|', 1)
        url = f"http://{HOST}/{TOPIC}"
        print(f"[NTFY] Posted \"{msg}\" to listeners")
        requests.post(url, data=msg)