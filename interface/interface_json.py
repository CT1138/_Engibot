import json
import requests

class IF_JSON:
    def __init__(self, path="", url="", json={}):
        self.json = {}

        if path:
            self.path = path
            self.json = self._loadFromPath()
        elif url:
            self.url = url
            self.json = self._loadFromURL()
        elif json is not None:
            self.json = json
        else:
            raise SyntaxError("[JSON] A type was not found or not specified!")

    def _loadFromPath(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                self.json = file
                return json.load(file)
        except FileNotFoundError:
            print(f"[JSON] Error: File not found at '{self.path}'")
        except json.JSONDecodeError:
            print(f"[JSON] Error: Failed to decode JSON from '{self.path}'")
        return None

    def _loadFromURL(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[JSON] HTTP Request failed: {e}")
        except json.JSONDecodeError:
            print("[JSON] Error: Failed to decode JSON response")
        return None

    def addElement(self, file_path: str, key: str, value):
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"[JSON] Warning: File not found. A new one will be created at '{file_path}'")
        except json.JSONDecodeError:
            print(f"[JSON] Warning: Invalid JSON in file. It will be overwritten at '{file_path}'")

        data[key] = value

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"[JSON] Entry '{key}' added/updated successfully.")
        except Exception as e:
            print(f"[JSON] Failed to write to '{file_path}': {e}")

    def addList(self, file_path: str, key_path: list, item):
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"[JSON] Something went wrong...\n{e}")

        target = data
        try:
            for key in key_path[:-1]:
                target = target.setdefault(key, {})
            target_list = target.setdefault(key_path[-1], [])
            if not isinstance(target_list, list):
                print("[JSON] Error: Target is not a list.")
                return
            if item in target_list:
                raise ValueError("[JSON] Target is already in list!")
            target_list.append(item)
        except Exception as e:
            raise Exception(f"[JSON] Something went wrong...\n{e}")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[JSON] Failed to write to '{file_path}': {e}")

    def removeList(self, file_path: str, key_path: list, item):
        data = {}

        # Load existing JSON data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"[JSON] Something went wrong loading the file...\n{e}")

        # Navigate to the nested list
        try:
            target = data
            for key in key_path[:-1]:
                target = target.get(key, {})
            target_list = target.get(key_path[-1], [])

            if not isinstance(target_list, list):
                print("[JSON] Error: Target is not a list.")
                return

            if item not in target_list:
                raise ValueError("[JSON] Item not found in list!")

            target_list.remove(item)
        except Exception as e:
            raise Exception(f"[JSON] Something went wrong modifying the data...\n{e}")

        # Save the updated data
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[JSON] Failed to write to '{file_path}': {e}")