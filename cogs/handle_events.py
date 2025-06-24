import discord
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_json import IF_JSON
import interface.interface_response as uResponse
import util.utils_math as uMath
from interface.interface_guild import IF_Guild

CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hEvent(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_typing(channel: discord.TextChannel, user: discord.Member, when):
        if(user.bot) : return
        GUILD = IF_Guild(channel.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(channel.id)
        if not CHANNELTYPE == ChannelType.SILLY : return

        IGNORES = IF_JSON("./__data/ignores.json").json["ignores"]
        if user.id in IGNORES: return

        RESPONSE, URL = uResponse.getRandom("onSpeaking", user.display_name)
        if uMath.roll(GUILD.getChance("OnSpeaking"), "On Speaking"):
            await channel.send(RESPONSE)

    async def on_message_delete(message):
        # Dont react to bots deleting messages
        if message.author.bot : return
        if not message.guild : return
        GUILD = IF_Guild(message.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)
        if not CHANNELTYPE == ChannelType.SILLY : return
        # 20% chance to respond if a message is deleted
        if(uMath.roll(GUILD.getChance("OnDelete"))):
            RESPONSE, URL = uResponse.getRandom("onDelete")
            CONTENT = ""
            if(uMath.roll(50)):
                CONTENT = RESPONSE
            else:
                CONTENT = URL
            await message.channel.send(CONTENT)

async def setup(bot):
    await bot.add_cog(hEvent(bot))