import util.utils_json as ujReader
import util.utils_cache as uCache
import discord
# Data
uCache.starboard_load()
CONFIG = ujReader.read("./__data/config.json")
# SETUP

# VARIABLES
STARBOARD_EMOJI = CONFIG["emojis"]["starboard"]
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]

async def _starboard_cache(bot):
    CHANNELS = ujReader.read("./__data/channels.json")
    for channel_id in CHANNELS["art"]:
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f"[LOG] Channel ID {channel_id} not found or not cached")
            continue
        print(f"[LOG] Scanning channel: {channel.name}")

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
