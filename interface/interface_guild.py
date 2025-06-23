import os
import shutil
import discord
from enum import Enum
import json
from interface.interface_json import IF_JSON

class ChannelType(Enum):
    STARBOARD = 0,
    ART = 1,
    SILLY = 2,
    STAFF = 3,
    STAFFLOG = 4,
    IGNORE = 5

class IF_Guild:
    def __init__(self, guild: discord.Guild):
        # Store Guild Data
        self.cache =  { "name": "", "members": [], "roles": [], "channels": [] }
        self.guild = guild
        self.guildID = guild.id
        self.guildName = guild.name
        self.guildRoles = guild.roles
        self.guildOwner = guild.owner
        self.guildChannels = guild.text_channels
        self.guildCategories = guild.categories
        print(f"[GUILD] Loading guild \'{self.guildName}\' (ID: {self.guildID}) owned by {self.guildOwner.name} (ID: {self.guildOwner.id})")

        # Get Guild Config
        CONFIGPATH = "./__data/guild/" + f"g_{self.guildID}.json"
        TEMPLATEPATH = "./__data/guild/g_template.json"
        if not os.path.exists(CONFIGPATH):
            print(f"[GUILD] Config for guild \'{self.guildName}\' not found, creating a new config based on template.")
            shutil.copy(TEMPLATEPATH, CONFIGPATH)
            print(f"[GUILD] Created new config for guild \'{self.guildName}\' from template.")

        self.guildConfig = IF_JSON(CONFIGPATH).json
        TEMPLATE = IF_JSON(TEMPLATEPATH).json
        self._config_was_updated = False
        self.guildConfig = self._merge_template(TEMPLATE, self.guildConfig)

        if self._config_was_updated:
            with open(CONFIGPATH, "w") as f:
                json.dump(self.guildConfig, f, indent=4)
        
        self._sync_config()
        self._cache()

    def _sync_config(self):
        current_name = self.guildConfig.get("name", "ERROR")
        if current_name != self.guildName:
            print(f"[GUILD] Syncing config: updating name from '{current_name}' to '{self.guildName}'")
            self.guildConfig["name"] = self.guildName
            self.guildConfig["id"] = self.guildID

            CONFIGPATH = f"./__data/guild/g_{self.guildID}.json"
            with open(CONFIGPATH, "w") as f:
                json.dump(self.guildConfig, f, indent=4)
        
    def _merge_template(self, template: dict, config: dict) -> dict:
        """Return a new config dict ordered like template, filling in missing keys."""
        merged = {}
        updated = False

        for key, tmpl_value in template.items():
            if key in config:
                cfg_value = config[key]
                # Recurse if both are dicts
                if isinstance(tmpl_value, dict) and isinstance(cfg_value, dict):
                    merged[key] = self._merge_template(tmpl_value, cfg_value)
                else:
                    merged[key] = cfg_value
            else:
                print(f"[GUILD] Adding missing key: {key}")
                merged[key] = tmpl_value
                updated = True

        # Preserve any extra keys that exist in config but not in template
        for key in config:
            if key not in merged:
                merged[key] = config[key]

        self._config_was_updated = updated or self._config_was_updated
        return merged
    
    def _cache(self):
        """Cache data"""
        CACHEPATH = "./__data/guild/cache/" + f"c_{self.guild.id}.json"
        TEMPLATEPATH = "./__data/guild/cache/" + f"c_template.json"
        if not os.path.exists(CACHEPATH):
            print(f"[GUILD] Cache for guild \'{self.guildName}\' not found, creating a new Cache based on template.")
            shutil.copy(TEMPLATEPATH, CACHEPATH)
            print(f"[GUILD] Created new Cache for guild \'{self.guildName}\' from template.")

        self.cache["name"] = self.guild.name
        self.cache["members"] = [str(member.id) for member in self.guild.members]
        self.cache["roles"] = [str(role.id) for role in self.guild.roles]
        self.cache["channels"] = [str(channel.id) for channel in self.guild.text_channels]

        with open(CACHEPATH, "w") as f:
            json.dump(self.cache, f, indent=4)
    
    def getChannelByID(self, id: int):
        return self.guild.get_channel(id)
        
    def getChannelByType(self, type: ChannelType, index = 0) -> discord.abc.GuildChannel:
        channel_config = self.guildConfig.get("channel", {})

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
        
        CHANNELID = channel_config.get(config_key, [])
        return self.guild.get_channel(CHANNELID[index - 1])
    
    def getChannelsOfType(self, type: ChannelType) -> list[discord.abc.GuildChannel]:
        channel_config = self.guildConfig.get("channel", {})

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
            list = self.guildConfig.get("channel", {}).get(key, [])
            if id in list:
                return enum_type
            return None
        
    def getPrefix(self) -> str:
        return self.guildConfig.get("command-prefix", "!")

    def isStaff(self, user_id: int) -> bool:
        staff_role_id = self.guildConfig.get("role", {}).get("staff")
        if staff_role_id is None:
            return False

        member = self.guild.get_member(user_id)
        if not member:
            return False

        return any(role.id == staff_role_id for role in member.roles)
    
    def getChance(self, key: str) -> int:
        return self.guildConfig.get("chances", {}).get(key, 100)