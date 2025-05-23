import json
import requests

def read(file_path: str):
    """Reads JSON data from a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'")
    return None

def readURL(url: str):
    """Fetches JSON data from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response")
    return None

def addElement(file_path: str, key: str, value):
    """Adds or updates a key-value pair in a JSON file."""
    data = {}

    # Try to read existing JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found. A new one will be created at '{file_path}'")
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in file. It will be overwritten at '{file_path}'")

    # Update or add the new entry
    data[key] = value

    # Write the updated data back to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Entry '{key}' added/updated successfully.")
    except Exception as e:
        print(f"Failed to write to '{file_path}': {e}")

def addList(file_path: str, key_path: list, item):
    data = {}

    # Load existing JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Something went wrong...\n{e}")

    # Navigate to the nested list
    target = data
    try:
        for key in key_path[:-1]:
            target = target.setdefault(key, {})
        target_list = target.setdefault(key_path[-1], [])
        if not isinstance(target_list, list):
            print("Error: Target is not a list.")
            return
        if item in target_list:
            raise ValueError("Target is already in list!")
        target_list.append(item)
    except Exception as e:
        raise Exception(f"Something went wrong...\n{e}")

    # Save the updated data
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to write to '{file_path}': {e}")

def removeList(file_path: str, key_path: list, item):
    data = {}

    # Load existing JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        raise Exception(f"Something went wrong loading the file...\n{e}")

    # Navigate to the nested list
    try:
        target = data
        for key in key_path[:-1]:
            target = target.get(key, {})
        target_list = target.get(key_path[-1], [])

        if not isinstance(target_list, list):
            print("Error: Target is not a list.")
            return

        if item not in target_list:
            raise ValueError("Item not found in list!")

        target_list.remove(item)
    except Exception as e:
        raise Exception(f"Something went wrong modifying the data...\n{e}")

    # Save the updated data
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to write to '{file_path}': {e}")