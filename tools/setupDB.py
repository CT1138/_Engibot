import json
import mysql.connector

# --- Configuration ---
with open("./__data/tokens.json", "r", encoding="utf-8") as f:
    DBCONFIG = json.load(f)["mariadb"]
    pass

# --- Load JSON Data ---
JSON_PATH = "./__data/responses.json"
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Connect to MySQL ---
conn = mysql.connector.connect(**DBCONFIG)
cursor = conn.cursor()

# --- Prepare Insert Queries ---
response_query = "INSERT INTO responses (`key`, content) VALUES (%s, %s)"
url_query = "INSERT INTO urls (`key`, content) VALUES (%s, %s)"

# --- Insert Data ---
for key, values in data.items():
    for response in values.get("_responses", []):
        cursor.execute(response_query, (key, response))
    for url in values.get("_urls", []):
        cursor.execute(url_query, (key, url))

# --- Finalize ---
conn.commit()
cursor.close()
conn.close()

print("Import complete.")
