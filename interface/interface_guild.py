import discord
from enum import Enum
import json
from sql.SQLCommands import SQLCommands
from interface.interface_database import IF_Database

class ChannelType(Enum):
    STARBOARD = 0,
    ART = 1,
    SILLY = 2,
    STAFF = 3,
    STAFFLOG = 4,
    IGNORE = 5,
    QUOTEBOOK = 6

TYPEMAPPING = {
    ChannelType.QUOTEBOOK: "quotebook",
    ChannelType.STARBOARD: "starboard",
    ChannelType.ART: "art",
    ChannelType.SILLY: "silly",
    ChannelType.STAFF: "staff",
    ChannelType.STAFFLOG: "staff-log",
    ChannelType.IGNORE: "ignore"
}

# Template Config
TEMPLATE = {
    "name": "template",
    "id": 1,
    "command-prefix": "!",
    "embed-color": "FF5733",
    "moderation": True,
    "scrapegifs": True,
    "chatcompletions": False,
    "sensitive_content": ["hate", "harassment", "sexual", "self-harm"],
    "chances": { "OnSpeaking": 95, "OnDelete": 80, "BroWent": 10, "Response": 95 },
    "channel": { "Quotebook": [], "whitelist": True, "blacklist": False, "starboard": [], "art": [], "silly": [], "staff-log": [], "ignore": []},
    "role": { "staff": 1, "owner": 0 },
    "member": { "thoustCreatoreth": 752989978535002134 }
}

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
        # print(f"[GUILD] Loading guild '{self.guildName}' (ID: {self.guildID}) owned by {self.guildOwner.name} (ID: {self.guildOwner.id})")

        # Init DB
        self.db = IF_Database()
        await self.db.connect()
        # Load Config from DB
        self.Config = await self.loadConfig()
        await self._sync_dbconfig()
        
    async def _sync_dbconfig(self):
        # Pull current DB config
        await self.db.connect()
        result = self.db.fetch(SQLCommands.GET_GUILD_CONFIG.value, (self.guildID,))

        if not result:
            print(f"[GUILD] No DB config found for guild {self.guildID}, inserting template config.")
            insert_query = SQLCommands.INSERT_GUILD_CONFIG.value
            params = (
                self.guildID,
                TEMPLATE["name"],
                TEMPLATE["command-prefix"],
                TEMPLATE["embed-color"],
                int(TEMPLATE["moderation"]),
                int(TEMPLATE["scrapegifs"]),
                int(TEMPLATE["chatcompletions"]),
                json.dumps(TEMPLATE["sensitive_content"]),
                json.dumps(TEMPLATE["chances"]),
                json.dumps(TEMPLATE["channel"]),
                json.dumps(TEMPLATE["role"]),
                json.dumps(TEMPLATE["member"]),
            )
            self.db.query(insert_query, params)
            self.Config = TEMPLATE
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
                    "sensitive_content": json.loads(result["sensitive_content"] or "[]"),
                    "chances": json.loads(result["chances"] or "{}"),
                    "channel": json.loads(result["channels"] or "{}"),
                    "role": json.loads(result["roles"] or "{}"),
                    "member": json.loads(result["members"] or "{}")
                }
            except Exception as e:
                print(f"[GUILD] Error loading DB config JSON fields: {e}")
                self.Config = TEMPLATE

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
                "sensitive_content": json.loads(result["sensitive_content"] or "[]"),
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

        config_key = TYPEMAPPING.get(type)
        if config_key is None:
            return []
        
        channel_ids = channel_config.get(config_key, [])
        return self.guild.get_channel(channel_ids[index])
    
    def getChannelsOfType(self, type: ChannelType) -> list[discord.abc.GuildChannel]:
        channel_config = self.Config.get("channel", {})

        config_key = TYPEMAPPING.get(type)
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
        for enum_type, key in TYPEMAPPING.items():
            channel_list = self.Config.get("channel", {}).get(key, [])
            if id in channel_list:
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
    
    async def setChannelType(self, channel_id: int, channel_type: ChannelType) -> bool:
        config_key = TYPEMAPPING.get(channel_type)
        if config_key is None:
            return False

        channels = self.Config.get("channel", {}).get(config_key, [])

        if channel_id in channels:
            # Already present
            return False

        channels.append(channel_id)
        self.Config["channel"][config_key] = channels

        return await self._saveChannelsConfig()

    async def unsetChannelType(self, channel_id: int, channel_type: ChannelType) -> bool:
        config_key = TYPEMAPPING.get(channel_type)
        if config_key is None:
            return False

        channels = self.Config.get("channel", {}).get(config_key, [])

        if channel_id not in channels:
            # Not present
            return False

        channels.remove(channel_id)
        self.Config["channel"][config_key] = channels

        return await self._saveChannelsConfig()

    async def _saveChannelsConfig(self) -> bool:
        try:
            # Ensure DB connected
            await self.db.connect()

            channels_json = json.dumps(self.Config.get("channel", {}))
            query = SQLCommands.UPDATE_GUILD_CONFIG.value.format("channels = %s")
            self.db.query(query, (channels_json, self.guildID))
            return True
        except Exception as e:
            print(f"[GUILD] Failed to save channel config: {e}")
            return False