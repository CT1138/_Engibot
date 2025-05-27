import discord
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import actions.Response as uResponse
import util.utils_math as uMath

CONFIG = ujReader.read("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG["emojis"]["starboard"]
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]

class hEvent(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_typing(channel, user: discord.Member, when):
        if(user.bot) : return
        IGNORES = ujReader.read("./__data/ignores.json")["ignores"]
        if user.id in IGNORES: return

        RESPONSE, URL = uResponse.getRandom("onSpeaking", user.display_name)
        if uMath.roll(95, "On Speaking"):
            await channel.send(RESPONSE)

    async def on_message_delete(message):
        # Dont react to bots deleting messages
        if message.author.bot : return
        if not message.guild : return
        # 20% chance to respond if a message is deleted
        if(uMath.roll(80)):
            RESPONSE, URL = uResponse.getRandom("onDelete")
            CONTENT = ""
            if(uMath.roll(50)):
                CONTENT = RESPONSE
            else:
                CONTENT = URL
            await message.channel.send(CONTENT)

async def setup(bot):
    await bot.add_cog(hEvent(bot))