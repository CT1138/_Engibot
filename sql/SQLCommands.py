from enum import Enum

class SQLCommands(Enum):
    GET_QUOTEBOOK = "SELECT * FROM quotebook WHERE `key` = %s"
    GET_MEMORY = "SELECT * FROM memories WHERE `key` = %s"
    GET_RESPONSES = "SELECT * FROM responses WHERE `key` = %s"
    GET_GIFS = "SELECT * FROM urls WHERE `key` = %s"
    INSERT_QUOTEBOOK = "INSERT INTO quotebook (`key`, content) VALUES (%s, %s)"
    INSERT_MEMORY = "INSERT INTO memories (`key`, content) VALUES (%s, %s)"
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
    GET_ALL_IGNORED_USERS = "SELECT user_id FROM guild_user_flags WHERE guild_id = %s AND ignore_flag = 1"
    INSERT_MESSAGE = """
        INSERT INTO message_log (
            message_id, guild_id, guild_name, channel_id, channel_name,
            author_id, author_name, content, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE content = VALUES(content)
    """
    INSERT_IMAGE = "INSERT INTO images (guild_id, author_id, collection, filepath) VALUES (%s, %s, %s, %s)"
    GET_IMAGES_BY_COLLECTION = "SELECT * FROM images WHERE guild_id = %s AND collection = %s"
    GET_ALL_COLLECTIONS = "SELECT DISTINCT collection FROM images WHERE guild_id = %s"