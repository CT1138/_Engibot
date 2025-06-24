import os
import shutil
import discord
from enum import Enum
import json
from interface.interface_json import IF_JSON
from interface.interface_database import IF_Database, SQLCommands

class ChannelType(Enum):
    STARBOARD = 0,
    ART = 1,
    SILLY = 2,
    STAFF = 3,
    STAFFLOG = 4,
    IGNORE = 5

class IF_Guild:
    def __init__(self, guild: discord.Guild):
        # Basic Guild Data
        self.guild = guild
        self.guildID = guild.id
        self.guildName = guild.name
        self.guildRoles = guild.roles
        self.guildOwner = guild.owner
        self.guildChannels = guild.text_channels
        self.guildCategories = guild.categories

        # DB & Config placeholders
        self.db = None
        self.cache = {"name": "", "members": [], "roles": [], "channels": []}
        self.Config = {}

    async def initialize(self):
        print(f"[GUILD] Loading guild '{self.guildName}' (ID: {self.guildID}) owned by {self.guildOwner.name} (ID: {self.guildOwner.id})")

        # Init DB
        self.db = IF_Database()
        msg = await self.db.connect()
        if "Error" in msg:
            print(msg)
            return
        # Load Config from DB
        self.Config = await self.loadConfig()
        await self._sync_dbconfig()
        
    async def _sync_dbconfig(self):
        # Pull current DB config
        await self.db.connect()
        result = self.db.fetch(SQLCommands.GET_GUILD_CONFIG.value, (self.guildID,))

        # Template
        template_config = {
            "name": "template",
            "id": 1,
            "command-prefix": "!",
            "embed-color": "FF5733",
            "moderation": True,
            "scrapegifs": True,
            "chatcompletions": False,
            "sensitive-content": ["hate", "harassment", "sexual", "self-harm"],
            "chances": { "OnSpeaking": 95, "OnDelete": 80, "BroWent": 10, "Response": 95 },
            "channel": { "whitelist": True, "blacklist": False, "starboard": [], "art": [], "silly": [], "staff-log": [], "ignore": []},
            "role": { "staff": 1, "owner": 0 },
            "member": { "thoustCreatoreth": 752989978535002134 }
        }
        if not result:
            print(f"[GUILD] No DB config found for guild {self.guildID}, inserting template config.")
            insert_query = SQLCommands.INSERT_GUILD_CONFIG.value
            params = (
                self.guildID,
                template_config["name"],
                template_config["command-prefix"],
                template_config["embed-color"],
                int(template_config["moderation"]),
                int(template_config["scrapegifs"]),
                int(template_config["chatcompletions"]),
                json.dumps(template_config["sensitive-content"]),
                json.dumps(template_config["chances"]),
                json.dumps(template_config["channel"]),
                json.dumps(template_config["role"]),
                json.dumps(template_config["member"]),
            )
            self.db.query(insert_query, params)
            self.Config = template_config
        else:
            try:
                self.Config = {
                    "name": result["name"],
                    "id": result["id"],
                    "command-prefix": result["command_prefix"],
                    "embed-color": result["embed_color"],
                    "moderation": bool(result["moderation"]),
                    "scrapegifs": bool(result["scrapegifs"]),
                    "chatcompletions": bool(result["chatcompletions"]),
                    "sensitive-content": json.loads(result["sensitive_content"] or "[]"),
                    "chances": json.loads(result["chances"] or "{}"),
                    "channel": json.loads(result["channels"] or "{}"),
                    "role": json.loads(result["roles"] or "{}"),
                    "member": json.loads(result["members"] or "{}")
                }
            except Exception as e:
                print(f"[GUILD] Error loading DB config JSON fields: {e}")
                self.Config = template_config

    async def loadConfig(self) -> dict:
        await self.db.connect()
        result = self.db.fetch(SQLCommands.GET_GUILD_CONFIG.value, (self.guildID,))
        if not result:
            print(f"[GUILD] No database config found for guild {self.guildID}")
            return {}
        try:
            config = {
                "name": result["name"],
                "id": result["id"],
                "command-prefix": result["command_prefix"],
                "embed-color": result["embed_color"],
                "moderation": bool(result["moderation"]),
                "scrapegifs": bool(result["scrapegifs"]),
                "chatcompletions": bool(result["chatcompletions"]),
                "sensitive-content": json.loads(result["sensitive_content"] or "[]"),
                "chances": json.loads(result["chances"] or "{}"),
                "channel": json.loads(result["channels"] or "{}"),
                "role": json.loads(result["roles"] or "{}"),
                "member": json.loads(result["members"] or "{}")
            }
            return config
        except Exception as e:
            print(f"[GUILD] Error decoding DB config: {e}")
            return {}

    def getChannelByID(self, id: int):
        return self.guild.get_channel(id)
        
    def getChannelByType(self, type: ChannelType, index = 0) -> discord.abc.GuildChannel:
        channel_config = self.Config.get("channel", {})

        # Map enum to config key
        type_mapping = {
            ChannelType.STARBOARD: "starboard",
            ChannelType.ART: "art",
            ChannelType.SILLY: "silly",
            ChannelType.STAFF: "staff",
            ChannelType.STAFFLOG: "staff-log",
            ChannelType.IGNORE: "ignore"
        }

        config_key = type_mapping.get(type)
        if config_key is None:
            return []
        
        channel_ids = channel_config.get(config_key, [])
        if index < 1 or index > len(channel_ids):
            return None
        return self.guild.get_channel(channel_ids[index - 1])
    
    def getChannelsOfType(self, type: ChannelType) -> list[discord.abc.GuildChannel]:
        channel_config = self.Config.get("channel", {})

        # Map enum to config key
        type_mapping = {
            ChannelType.STARBOARD: "starboard",
            ChannelType.ART: "art",
            ChannelType.SILLY: "silly",
            ChannelType.STAFF: "staff",
            ChannelType.STAFFLOG: "staff-log",
            ChannelType.IGNORE: "ignore"
        }

        config_key = type_mapping.get(type)
        if config_key is None:
            return []
        
        channel_ids = channel_config.get(config_key, [])
        channels = []

        for ID in channel_ids:
            channel = self.guild.get_channel(ID)
            if channel:
                channels.append(channel)

        return channels

    def getRoleByID(self, id: int) -> int:
        return self.guild.get_role(id)
    
    def getChannelType(self, id: int) -> ChannelType:
        type_mapping = {
            "starboard": ChannelType.STARBOARD,
            "art": ChannelType.ART,
            "silly": ChannelType.SILLY,
            "staff": ChannelType.STAFF,
            "staff-log": ChannelType.STAFFLOG,
            "ignore": ChannelType.IGNORE
        }
        for key, enum_type in type_mapping.items():
            list = self.Config.get("channel", {}).get(key, [])
            if id in list:
                return enum_type
            return None
        
    def getPrefix(self) -> str:
        return self.Config.get("command-prefix", "!")

    def isStaff(self, user_id: int) -> bool:
        staff_role_id = self.Config.get("role", {}).get("staff")
        if staff_role_id is None:
            return False

        member = self.guild.get_member(user_id)
        if not member:
            return False

        return any(role.id == staff_role_id for role in member.roles)
    
    def getChance(self, key: str) -> int:
        return self.Config.get("chances", {}).get(key, 100)