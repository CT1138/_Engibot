import os
import sys
import discord
import datetime
import aimoderator
from interface.interface_guild import IF_Guild, ChannelType
from discord import utils as dUtils, File, app_commands
from discord.ext import commands as dCommands
from interface.interface_json import IF_JSON
import interface.interface_response as uResponse

# Read Configs
CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hStaff(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_json_choices(self):
        path = "./__data/"
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(path)
            if f.endswith(".json") and f != "tokens.json"
        ]

    # Content Filter
    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        GUILD = IF_Guild(message.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)
        if CHANNELTYPE == ChannelType.STAFF : return
        if CHANNELTYPE == ChannelType.IGNORE : return
        if message.author.bot : return

        # If the AI flags a message - We trust this less so it will only log the incident, action will not be taken.
        moderator = aimoderator.AIModerator(message.guild)
        await moderator.initialize()
        await moderator.GUILD.initialize()
        flagged, aiflagged, response = moderator.scanText(message.content)
        if aiflagged:
            STAFFLOG = GUILD.getChannelByType(ChannelType.STAFFLOG)
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

            await STAFFLOG.send(embed=embed)

        # If it is flagged by our guidelines too, we delete the message
        if flagged :
            print("flagged")
            # Delete and message user
            # await message.delete()
            await message.channel.send(f"{message.author.mention} your message has been flagged by my moderation engine, if you believe this was wrong, ping a <@&1372047838770626640> member and they may review this incident.")
            return

    # Pure slash command: kill
    @app_commands.command(name="kill", description="Shut down the bot")
    async def kill(self, interaction: discord.Interaction):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        GUILD = IF_Guild(interaction.guild)
        await GUILD.initialize()
        if GUILD.isStaff(interaction.user.id):
            await interaction.response.send_message("Shutting down...", ephemeral=True)
            await self.bot.close()
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)

    # Pure slash command: restart
    @app_commands.command(name="restart", description="Restart the bot")
    async def restart(self, interaction: discord.Interaction):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        GUILD = IF_Guild(interaction.guild)
        await GUILD.initialize()
        if GUILD.isStaff(interaction.user.id):
            await interaction.response.send_message("Restarting...", ephemeral=True)
            await self.bot.close()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)

async def setup(bot):
    await bot.add_cog(hStaff(bot))
