# Functionally empty for now until I get my raspberry pi setup with mariadb
# TODO: Write interface
# TODO: As interface is implemented, write specialized getters and setters for common operations
import mariadb
from enum import Enum
from mariadb import Error
from interface.interface_json import IF_JSON
TOKENS = IF_JSON("./__data/tokens.json").json

class SQLCommands(Enum):
    GET_RESPONSES = "SELECT * FROM responses WHERE `key` = %s"
    GET_GIFS = "SELECT * FROM urls WHERE `key` = %s"
    INSERT_RESPONSE = "INSERT INTO responses (`key`, content) VALUES (%s, %s)"
    INSERT_GIF = "INSERT INTO urls (`key`, content) VALUES (%s, %s)"
    GET_GUILD_CONFIG = "SELECT * FROM guild_config WHERE id = %s"
    INSERT_GUILD_CONFIG = """
        INSERT INTO guild_config (
            id, name, command_prefix, embed_color, moderation, scrapegifs, chatcompletions,
            sensitive_content, chances, channels, roles, members
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    UPDATE_GUILD_CONFIG = "UPDATE guild_config SET {} WHERE id = %s"
    DELETE_GUILD_CONFIG = "DELETE FROM guild_config WHERE id = %s"
    GET_USER_FLAG = "SELECT ignore_flag FROM guild_user_flags WHERE guild_id = %s AND user_id = %s"
    SET_USER_FLAG = """
        INSERT INTO guild_user_flags (guild_id, user_id, ignore_flag)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE ignore_flag = VALUES(ignore_flag)
    """
    DELETE_USER_FLAG = "DELETE FROM guild_user_flags WHERE guild_id = %s AND user_id = %s"
    GET_ALL_IGNORED_USERS = "SELECT user_id FROM guild_user_flags WHERE guild_id = %s AND ignore_flag = 1",
    INSERT_MESSAGE = """
        INSERT INTO message_log (
            message_id, guild_id, guild_name, channel_id, channel_name,
            author_id, author_name, content, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE content = VALUES(content)
    """


class IF_Database:
    def __init__(self):
        self.config = {
            'host': TOKENS["MySQL"]["host"],
            'user': TOKENS["MySQL"]["user"],
            'password': TOKENS["MySQL"]["password"],
            'database': TOKENS["MySQL"]["database"],
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.connection = None
        self.cursor = None

    async def connect(self):
        try:
            self.connection = mariadb.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            msg = "[DB] Successfully connected to MariaDB."
            return msg
        except Error as e:
            msg = f"[DB] Error connecting to MariaDB: {e}"
            print(msg)
            return msg

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("[DB] Query executed successfully.")
        except Error as e:
            print(f"[DB] Error executing query: {e}")
            self.connection.rollback()

    def fetch(self, query, params=None, all=False):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall() if all else self.cursor.fetchone()
        except Error as e:
            print(f"[DB] Error fetching data: {e}")
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

    def __del__(self):
        self.disconnect()
