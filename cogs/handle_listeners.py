import discord
from discord.ext import commands as dCommands
import actions.Replies as uReply
import actions.Response as uResponse
import util.utils_json as ujReader
import util.utils_cache as uCache
import actions
import aimoderator
import datetime

moderator = aimoderator.AIModerator()
CONFIG = ujReader.read("./__data/config.json")
CHANNELS = ujReader.read("./__data/channels.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG["emojis"]["starboard"]
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]
STAFFLOG = CHANNELS["staff-log"]

class hListener(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        CHANNELS = ujReader.read("./__data/channels.json")
        IGNORES = ujReader.read("./__data/ignores.json")["ignores"]

        # Do not do anything if :
        if message.author.id in IGNORES: return # author is in ignore list
        if message.channel.id in CHANNELS: return # channel is not in valid channels list
        if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        if message.content.startswith(PREFIX) : return # message is a command

        flagged, aiflagged, response = moderator.scanText(message.content)
    
        # If the AI flags a message - We trust this less so it will only log the incident, action will not be taken.
        if aiflagged:
            # if not any(role.id == 1372047838770626640 for role in message.author.roles):
            if not message.author.id == 1058073516186026095:
                StaffChannel = self.bot.get_channel(STAFFLOG)

                embed = discord.Embed(
                    title="Flagged Message",
                    description=
                    f"""Posted in {message.channel.mention}
                    Content: {message.content}"""
                    ,
                    colour=0xf50031,
                    timestamp=datetime.datetime.now(),
                    url=message.jump_url
                )
                embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                embed.set_footer(text="Moderation")

                result = response.results[0]

                categories = result.categories.model_dump() 
                scores = result.category_scores.model_dump()

                for cat, f in categories.items():
                    if not f : continue
                    score = scores.get(cat, 0)
                    embed.add_field(
                        name=f"{cat}",
                        value=f"Score: {score:.3f}",
                        inline=True
                    )

                await StaffChannel.send(embed=embed)

        # If it is flagged by our guidelines too, we delete the message
        if flagged :
            # if not any(role.id == 1372047838770626640 for role in message.author.roles):
            if not message.author.id == 1058073516186026095:
                print("flagged")
                # Delete and message user
                # await message.delete()
                await message.channel.send(f"{message.author.mention} your message has been flagged by my moderation engine, if you believe this was wrong, ping a <@&1372047838770626640> member and they may review this incident.")
                return

        if message.attachments:
            if message.channel.id in CHANNELS["art"]:
                await message.add_reaction("<:happi:1355706814083371199>")
                await message.add_reaction(STARBOARD_EMOJI)


        await uReply.reply_random(message)
        await uReply.reply_bro(message)

    @dCommands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Return if the user is a bot or if there is no image or the image is not in our art channel
        CHANNELS = ujReader.read("./__data/channels.json")
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
