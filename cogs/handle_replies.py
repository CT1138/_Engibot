import discord
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
import interface.interface_response as IF_RESPONSE
from interface.interface_json import IF_JSON
import util.utils_math as uMath


CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hReplies(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        GUILD = IF_Guild(message.channel.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)
        
        # Do not do anything if :
        if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        if not CHANNELTYPE == ChannelType.SILLY : return

        RESPONSE, URL = IF_RESPONSE.getRandom("random")
        CHANCE = GUILD.getChance("Response")

        if uMath.roll(CHANCE, "Response"):
            if(uMath.roll(80, "Send All")):
                # 20% Chance to send RESPONSE & URL
                await message.channel.send(RESPONSE)
                await message.channel.send(URL)
            else:
                # 80% Chance to only send GIF or RESPONSE
                if(uMath.roll(50, "Send Gif or Response")) :    
                    await message.channel.send(URL)
                else:                               
                    await message.channel.send(RESPONSE)

async def setup(bot):
    await bot.add_cog(hReplies(bot))
