import discord
import util.utils_cache as uCache
import json
import os
from interface.interface_json import IF_JSON
from interface.interface_guild import IF_Guild, ChannelType

# Data
uCache.starboard_load()
CONFIG = IF_JSON(path="./__data/config.json")

# VARIABLES
STAR_SAVEPATH = "./__data/starboard_cache.json"
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

async def _starboard_cache(bot: discord.Client):
    for guild in bot.guilds :
        GUILD = IF_Guild(guild)
        CHANNELS = GUILD.getChannelsOfType(ChannelType.ART)
        for channel in CHANNELS:
            if channel is None:
                print(f"[STARBOARD] Channel ID {channel} not found or not cached")
                continue
            print(f"[STARBOARD] Scanning channel: {channel.name}")

            try:
                async for message in channel.history(limit=None, oldest_first=True):
                    MESSAGE_ID = str(message.id)
                    if MESSAGE_ID in uCache.starred_messages:
                        continue

                    if message.attachments:
                        has_image = any(
                            att.content_type and att.content_type.startswith("image/")
                            for att in message.attachments
                        )
                        if has_image:
                            message_id_str = str(message.id)

                            # Check if already reacted with the star emoji by anyone
                            star_reaction = next((r for r in message.reactions if r.emoji == STARBOARD_EMOJI), None)

                            if star_reaction:
                                # Add to cache if not already cached
                                if message_id_str not in uCache.starred_messages:
                                    print(f"Message {message.id} already has {star_reaction.count} stars; caching it.")
                                    uCache.starred_messages[message_id_str] = star_reaction.count
                                    uCache.starboard_save()
                            else:
                                try:
                                    await message.add_reaction(STARBOARD_EMOJI)
                                    print(f"Starred message {message.id} in #{channel.name}")
                                    uCache.starred_messages[message_id_str] = 1
                                    uCache.starboard_save()
                                except Exception as e:
                                    print(f"Failed to react to message {message.id}: {e}")

            except Exception as e:
                print(f"Failed to read history in {channel.name}: {e}")

def starboard_save():
    with open(STAR_SAVEPATH, "w") as f:
        json.dump(starred_messages, f)

def starboard_load():
    global starred_messages
    if os.path.exists(STAR_SAVEPATH):
        with open(STAR_SAVEPATH, "r") as f:
            starred_messages = json.load(f)
    else:
        starred_messages = {}
