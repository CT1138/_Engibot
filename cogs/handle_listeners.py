import discord
import re
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_database import IF_Database, SQLCommands
import interface.interface_response as uResponse
from interface.interface_json import IF_JSON
from aimoderator import AIChatbot
import util.utils_cache as uCache

CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hListener(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        
        # Starboard features
        if message.attachments:
            if CHANNELTYPE == ChannelType.ART:
                await message.add_reaction("<:happi:1355706814083371199>")
                await message.add_reaction(STARBOARD_EMOJI)

        url_pattern = re.compile(r"https?://(?:www\.)?tenor\.com[^\s]*")
        if url_pattern.search(message.content) and GUILD.Config["scrapegifs"]:
            link = re.findall(url_pattern, message.content)[0]
            uResponse.add("random", False, link)
            print(f"[RESPONSE] scalped and found gif {link}")

        if GUILD.Config["chatcompletions"]:
            Chatterbox = AIChatbot(f"You are an observer of a discord conversation in a server called {GUILD.guildName}")
            Context = await Chatterbox.channelToGPT(message.channel)
            Completion = Chatterbox.chatCompletion(Context)
            print("[AI] " + Completion)

        DB.__del__()

    @dCommands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Return if the user is a bot or if there is no image or the image is not in our art channel
        CHANNELS = IF_JSON("./__data/channels.json")
        if(user.bot) : return
        if not reaction.message.attachments : return
        if not reaction.message.channel.id in CHANNELS.json["art"] : return

        # Variables
        MESSAGE = reaction.message
        MESSAGE_ID = MESSAGE.id
        MESSAGE_CONTENT = MESSAGE.content
        CHANNEL = MESSAGE.channel
        CHANNEL_ID = CHANNEL.id
        COUNT = reaction.count
        MILESTONES = {3, 5, 10, 15, 25, 50, 100}
        PREV_MILESTONE = uCache.starred_messages.get(str(MESSAGE_ID), 0)

        # Is this new reaction a star?
        for milestone in sorted(MILESTONES):
            RESPONSE, URL = uResponse.getRandom("starboardMilestone")
            if COUNT >= milestone > PREV_MILESTONE:
                uCache.starred_messages[MESSAGE_ID] = milestone
                uCache.starboard_save()
        
                # Build the embed to send
                AUTHOR = MESSAGE.author.name
                TITLE= f"Art by {AUTHOR}"
                if MESSAGE.content : TITLE = MESSAGE_CONTENT
                embed = discord.Embed(
                    title= TITLE,
                    url= MESSAGE.jump_url,
                    color= 0x4CE4B1,
                    timestamp= MESSAGE.created_at
                )
                embed.set_author(name= AUTHOR, icon_url= MESSAGE.author.avatar.url)
                embed.set_image(url= MESSAGE.attachments[0].url)

                # Send the art in every starboard channel
                for cID in CHANNELS.json["starboard"]:
                    c = self.bot.get_channel(cID)
                    if c.guild != CHANNEL.guild : continue
                    await c.send(embed=embed, content=f"{STARBOARD_EMOJI} {COUNT} | <#{CHANNEL_ID}>")

                # Reply in the art channel
                await MESSAGE.reply(RESPONSE)
                break

async def setup(bot):
    await bot.add_cog(hListener(bot))
