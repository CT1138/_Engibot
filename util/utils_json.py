import json
import requests
import os
import html

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

    
    def dumpHTML(json_path: str):
        # Ensure __tmp/ directory exists
        os.makedirs("__tmp", exist_ok=True)

        # Read JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Format as pretty JSON string
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)

        # Escape HTML characters for safe rendering
        escaped_json = html.escape(pretty_json)

        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>JSON Dump - {os.path.basename(json_path)}</title>
            <style>
                body {{
                    font-family: monospace;
                    background: #1e1e1e;
                    color: #dcdcdc;
                    padding: 1rem;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <h1>{os.path.basename(json_path)}</h1>
            <pre>{escaped_json}</pre>
        </body>
        </html>
        """

        # Build output filename
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        out_path = os.path.join("__tmp", f"{base_name}_dump.html")

        # Write to file
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return out_path