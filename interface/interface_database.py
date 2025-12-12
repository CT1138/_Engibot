import mariadb
import os
import sys
from datetime import datetime
from mariadb import Error
from sql.SQLCommands import SQLCommands

class IF_Database:
    def __init__(self):
        HOST = os.getenv("MARIADB_HOST", "localhost")
        USER = os.getenv("MARIADB_USERNAME", "engibot")
        PORT = int(os.getenv("MARIADB_PORT", 3306))
        PASSWORD=os.getenv("MARIADB_PASSWORD", "password")
        DATABASE=os.getenv("MARIADB_DATABASE", "engibot")
        self.config = {
            'host': HOST,
            'user': USER,
            'password': PASSWORD,
            'database': DATABASE,
            "unix_socket": None,
            'port': PORT
        }
        self.connection = None
        self.cursor = None

    async def connect(self):
        try:
            self.connection = mariadb.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            self.cursor.execute("SET NAMES utf8mb4;")
            self.cursor.execute("SET CHARACTER SET utf8mb4;")
            self.cursor.execute("SET character_set_connection=utf8mb4;")

            return True
        except Error as e:
            print(e)
            return True

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection:
                try:
                    if self.connection.is_connected():
                        self.connection.close()
                except Exception:
                    pass
                self.connection = None
        except Exception:
            pass

    def query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Error as e:
            msg = f"[DB] Error executing query: {e}"
            print(msg)
            self.connection.rollback()

    def fetch(self, query, params=None, all=False):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall() if all else self.cursor.fetchone()
        except Error as e:
            msg = f"[DB] Error fetching data: {e}"
            print(msg)
            return [] if all else None
    
    # Fetch a user's ignore flag status
    def isIgnored(self, guild_id: int, user_id: int) -> bool:
        result = self.fetch(SQLCommands.GET_USER_FLAG.value, (guild_id, user_id))
        if result:
            return bool(result["ignore_flag"])
        return False

    # Set (insert or update) a user's ignore flag
    def setIgnored(self, guild_id: int, user_id: int, ignore: bool):
        self.query(SQLCommands.SET_USER_FLAG.value, (guild_id, user_id, int(ignore)))

    # Delete a user's ignore flag entry
    def deleteIgnored(self, guild_id: int, user_id: int):
        self.query(SQLCommands.DELETE_USER_FLAG.value, (guild_id, user_id))

    # Get all user IDs flagged as ignored for a specific guild
    def getIgnoredUsers(self, guild_id: int) -> list[int]:
        rows = self.fetch(SQLCommands.GET_ALL_IGNORED_USERS.value, (guild_id,), all=True)
        return [row["user_id"] for row in rows] if rows else []
    
    async def addImage(self, attachment, guild_id: int, author_id: int, collection: str, path="/srv/engibot/images") -> str:
        guild_folder = os.path.join(path, str(guild_id), collection)
        os.makedirs(guild_folder, exist_ok=True)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"collection_{author_id}_{timestamp}_{attachment.filename.lower()}"
        full_path = os.path.join(guild_folder, filename)

        # Save the image
        await attachment.save(full_path)

        # Store relative path
        rel_path = os.path.relpath(full_path)

        # Insert into database
        self.query(SQLCommands.INSERT_IMAGE.value, (guild_id, author_id, collection, rel_path))

        return rel_path

    def getImagesByCollection(self, guild_id: int, collection: str) -> list[dict]:
        return self.fetch(SQLCommands.GET_IMAGES_BY_COLLECTION.value, (guild_id, collection), all=True)

    def getCollections(self, guild_id: int) -> list[str]:
        rows = self.fetch(SQLCommands.GET_ALL_COLLECTIONS.value, (guild_id,), all=True)
        return [row["collection"] for row in rows]

    def __del__(self):
        self.disconnect()