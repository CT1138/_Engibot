from discord.ext import commands as dCommands
from enum import Enum
from Discord import discord

class ChannelType(Enum):
    ORIGINAL=0,
    BACKUP=1,
    UNDEFINED=2

class hBackup(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def getType(id:int):
        return ChannelType.UNDEFINED

    @dCommands.hybrid_group(name="setup-backup", with_app_command=True, invoke_without_command=True)
    async def setup_backup(self, ctx):
        await ctx.send("goon")

    # Server Updated
    @dCommands.listener()
    async def on_guild_update(self, before: discord.abc.Guild, after: discord.abc.Guild):
        print(f"Guild Updated!\nBefore: {before}\nAfter: {after}")
        return

    # Channel Created
    @dCommands.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        print(f"Channel Created!\n{channel}")
        return

    # Channel Deleted
    @dCommands.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        print(f"Channel Deleted!\n{channel}")
        return

    # Channel Update
    @dCommands.listener()
    async def on_channel_update(self, before, after):
        print(f"Channel Update!\nBefore: {before}\nAfter: {after}")
        return

    # Role Created
    @dCommands.listener()
    async def on_role_create(self, role):
        print(f"Role Created!\n{role}")
        return

    # Role Deleted
    @dCommands.listener()
    async def on_role_delete(self, role):
        print(f"Role Deleted!\n{role}")
        return

    # Emoji update
    @dCommands.listener()
    async def on_guild_emojis_update(self, before, after):
        print(f"Emojis Updated!\nBefore: {before}\nAfter: {after}")
        return

async def setup(bot):
    await bot.add_cog(hBackup(bot))
