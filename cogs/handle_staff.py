import os
import sys
import discord
import datetime
import aimoderator
from interface.interface_guild import IF_Guild, ChannelType, TYPEMAPPING
from discord import utils as dUtils, File, app_commands
from discord.ext import commands as dCommands
from interface.interface_json import IF_JSON
from interface.interface_database import IF_Database, SQLCommands
from interface.interface_response import IF_Response, ResultType

# Read Configs
CONFIG = IF_JSON("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG.json["emojis"]["starboard"]
STATUS = CONFIG.json["status"]

class hStaff(dCommands.Cog):
    def __init__(self, bot):
        self.response = IF_Response()
        self.bot = bot

    @dCommands.hybrid_group(name="staff", with_app_command=True, invoke_without_command=True)
    async def staff(self, ctx):
        RESPONSE = await self.response.getRandom("failedKill", result_type=ResultType.RESPONSE)
        await ctx.send(RESPONSE)
        await ctx.defer()

    def get_json_choices(self):
        path = "./__data/"
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(path)
            if f.endswith(".json") and f != "tokens.json"
        ]
    
    def _get_channel_type(self, input_str: str) -> ChannelType | None:
        for ctype, name in TYPEMAPPING.items():
            if name.lower() == input_str.lower():
                return ctype
        return None
    
    def _format_available_types(self) -> str:
        return "\n".join(f"- {name}" for name in TYPEMAPPING.values())

    # Content Filter
    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Initialize guild
        GUILD = IF_Guild(message.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)

        # Do we even care about this message?
        if CHANNELTYPE == ChannelType.STAFF : return
        if CHANNELTYPE == ChannelType.IGNORE : return
        if message.author.bot : return
        if GUILD.isStaff(message.author.id) : return
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
            if flagged :
                await STAFFLOG.send("<@&1372047838770626640>")

    # Pure slash command: kill
    @staff.command(name="kill", description="Shut down the bot")
    async def kill(self, interaction: discord.Interaction):
        RESPONSE = self.response.getRandom("failedKill")
        GUILD = IF_Guild(interaction.guild)
        await GUILD.initialize()
        if GUILD.isStaff(interaction.user.id):
            await interaction.response.send_message("Shutting down...", ephemeral=True)
            await self.bot.close()
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)

    # Pure slash command: restart
    @staff.command(name="restart", description="Restart the bot")
    async def restart(self, interaction: discord.Interaction):
        RESPONSE = self.response.getRandom("failedKill")
        GUILD = IF_Guild(interaction.guild)
        await GUILD.initialize()
        if GUILD.isStaff(interaction.user.id):
            await interaction.response.send_message("Restarting...", ephemeral=True)
            await self.bot.close()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)


    @staff.command(name="cache-quotebook", description="Cache quotebook data")
    @app_commands.describe(limit="Number of messages to process (max 500)")
    async def cache_quotebook(self, ctx: dCommands.Context, limit: int):
        if limit < 1 or limit > 500:
            await ctx.send("Limit must be between 1 and 500.", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)

        guild = ctx.guild
        if guild is None:
            await ctx.send("This command can only be used in a guild.", ephemeral=True)
            return
        
        interface_guild = IF_Guild(guild)
        await interface_guild.initialize()

        if interface_guild.isStaff(ctx.author.id) is False:
            await ctx.send("You do not have permission to use this command.", ephemeral=True)
            return

        quotebook_channel = await interface_guild.getChannelByType(ChannelType.QUOTEBOOK)
        if quotebook_channel is None:
            await ctx.send("Quotebook channel not found.", ephemeral=True)
            return

        messages = await quotebook_channel.history(limit=limit).flatten()
        uploaded_count = 0

        for msg in messages:
            image_url = None
            if msg.attachments:
                for att in msg.attachments:
                    if att.content_type and att.content_type.startswith("image"):
                        image_url = att.url
                        break
            if not image_url and msg.embeds:
                for embed in msg.embeds:
                    if embed.image and embed.image.url:
                        image_url = embed.image.url
                        break

            starts_with_quote = msg.content.startswith('"') if msg.content else False

            if image_url or starts_with_quote:
                content_to_upload = image_url if image_url else msg.content
                try:
                    await interface_guild.db.query(
                        SQLCommands.INSERT_QUOTEBOOK,
                        (
                            msg.id,
                            interface_guild.guildID,
                            interface_guild.guildName,
                            msg.channel.id,
                            msg.channel.name,
                            msg.author.id,
                            msg.author.name,
                            content_to_upload,
                            msg.created_at,
                        ),
                    )
                    uploaded_count += 1
                except Exception as e:
                    print(f"Error uploading message {msg.id}: {e}")

        await ctx.send(f"Cached {uploaded_count} messages from the quotebook channel.", ephemeral=True)


    @staff.command(name="set-channel", description="Add the current channel to a channel type")
    @app_commands.describe(channel_type="Type of channel to set (quotebook, starboard, art, silly, staff, staff-log, ignore)")
    async def set_channel(self, ctx: dCommands.Context, channel_type: str = None):
        interface_guild = IF_Guild(ctx.guild)
        await interface_guild.initialize()

        if not interface_guild.isStaff(ctx.author.id):
            await ctx.send("You do not have permission to use this command.", ephemeral=True)
            return

        ctype = self._get_channel_type(channel_type)
        if ctype is None:
            available = self._format_available_types()
            await ctx.send(
                f"Invalid or missing channel type.\nAvailable types are:\n{available}", ephemeral=True
            )
            return

        success = await interface_guild.setChannelType(ctx.channel.id, ctype)
        if success:
            await ctx.send(f"Channel added to **{channel_type}** type.", ephemeral=True)
        else:
            await ctx.send(f"Channel is already part of **{channel_type}** or failed to add.", ephemeral=True)

    @staff.command(name="unset-channel", description="Remove the current channel from a channel type")
    @app_commands.describe(channel_type="Type of channel to remove (quotebook, starboard, art, silly, staff, staff-log, ignore)")
    async def unset_channel(self, ctx: dCommands.Context, channel_type: str = None):
        interface_guild = IF_Guild(ctx.guild)
        await interface_guild.initialize()

        if not interface_guild.isStaff(ctx.author.id):
            await ctx.send("You do not have permission to use this command.", ephemeral=True)
            return

        ctype = self._get_channel_type(channel_type)
        if ctype is None:
            available = self._format_available_types()
            await ctx.send(
                f"Invalid or missing channel type.\nAvailable types are:\n{available}", ephemeral=True
            )
            return

        success = await interface_guild.unsetChannelType(ctx.channel.id, ctype)
        if success:
            await ctx.send(f"Channel removed from **{channel_type}** type.", ephemeral=True)
        else:
            await ctx.send(f"Channel was not part of **{channel_type}** or failed to remove.", ephemeral=True)

    @staff.command(name="channel-info", description="Show which channel types the current channel belongs to")
    async def channel_info(self, ctx: dCommands.Context):
        interface_guild = IF_Guild(ctx.guild)
        await interface_guild.initialize()

        channel_id = ctx.channel.id
        channel_config = interface_guild.Config.get("channel", {})

        matching_types = []
        for ctype, key in TYPEMAPPING.items():
            if channel_id in channel_config.get(key, []):
                matching_types.append(key)

        if not matching_types:
            await ctx.send("This channel is not assigned to any special categories.", ephemeral=True)
        else:
            types_list = ", ".join(matching_types)
            await ctx.send(f"This channel belongs to the following categories:\n{types_list}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(hStaff(bot))
