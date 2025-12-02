import discord
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_response import IF_Response, ResultType
import util.utils_math as uMath

class hReplies(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response = IF_Response()

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild: return
        GUILD = IF_Guild(message.channel.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)
        
        # Do not do anything if :
        if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        if message.author.id == self.bot.user.id : return # message is from the bot itself
        
        if not CHANNELTYPE == ChannelType.SILLY : return

        RESPONSE = await self.response.getRandom("random" , result_type=ResultType.RESPONSE)
        URL = await self.response.getRandom("random", result_type=ResultType.URL)
        
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
