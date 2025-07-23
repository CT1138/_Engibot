import discord
import re
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_database import IF_Database, SQLCommands
from interface.interface_response import IF_Response
from interface.interface_json import IF_JSON
from interface.interface_openai import AIChatbot

CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hListener(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RESPONSE = IF_Response()

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        GUILD = IF_Guild(message.channel.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)

        DB = IF_Database()
        await DB.connect()

        params = (
            message.id,
            message.guild.id if message.guild else None,
            message.guild.name if message.guild else None,
            message.channel.id,
            message.channel.name,
            message.author.id,
            message.author.name,
            message.content,
            message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        DB.query(SQLCommands.INSERT_MESSAGE.value, params)

        # Do not do anything if :
        if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        if message.author.id == self.bot.user.id : return # message is from the bot itself
        # Starboard features
        if message.attachments:
            if CHANNELTYPE == ChannelType.ART:
                await message.add_reaction("<:happi:1355706814083371199>")
                await message.add_reaction(STARBOARD_EMOJI)

        url_pattern = re.compile(r"https?://(?:www\.)?tenor\.com[^\s]*")
        if url_pattern.search(message.content) and GUILD.Config["scrapegifs"]:
            link = re.findall(url_pattern, message.content)[0]
            await self.RESPONSE.add("random", link, result_type=IF_Response.ResultType.URL)
            print(f"[RESPONSE] scalped and found gif {link}")

        if GUILD.Config["chatcompletions"]:
            Chatterbox = AIChatbot(f"You are an observer of a discord conversation in a server called {GUILD.guildName}")
            Context = await Chatterbox.channelToGPT(message.channel)
            Completion = Chatterbox.chatCompletion(Context)
            print("[AI] " + Completion)

        DB.__del__()

async def setup(bot):
    await bot.add_cog(hListener(bot))
