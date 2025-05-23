import discord
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import util.Response as uResponse
import util.utils_cache as uCache
import actions

CONFIG = ujReader.read("./data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG["emojis"]["starboard"]
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]

class hListener(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        CHANNELS = ujReader.read("./data/channels.json")
        IGNORES = ujReader.read("./data/ignores.json")["ignores"]

        # Do not do anything if :
        if message.author.id in IGNORES: return # author is in ignore list
        if message.channel.id in CHANNELS: return # channel is not in valid channels list
        if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        if message.content.startswith(PREFIX) : return # message is a command

        if message.attachments:
            if message.channel.id in CHANNELS["art"]:
                await message.add_reaction("<:happi:1355706814083371199>")
                await message.add_reaction(STARBOARD_EMOJI)
                return

        await actions.Silly.reply_random(message)

    @dCommands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Return if the user is a bot or if there is no image or the image is not in our art channel
        CHANNELS = ujReader.read("./data/channels.json")
        if(user.bot) : return
        if not reaction.message.attachments : return
        if not reaction.message.channel.id in CHANNELS["art"] : return

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
                actions.uCache.starred_messages[MESSAGE_ID] = milestone
                actions.uCache.starboard_save()
        
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
                for cID in CHANNELS["starboard"]:
                    c = self.bot.get_channel(cID)
                    if c.guild != CHANNEL.guild : continue
                    await c.send(embed=embed, content=f"{STARBOARD_EMOJI} {COUNT} | <#{CHANNEL_ID}>")

                # Reply in the art channel
                await MESSAGE.reply(RESPONSE)
                break

async def setup(bot):
    await bot.add_cog(hListener(bot))
