import discord
from discord.ext import commands as dCommands
from interface.interface_ntfy import IF_NTFY


class hAudit(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def notify(self, message: str):
        IF_NTFY.post(message)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        entry = await self.get_latest_entry(guild, discord.AuditLogAction.ban)
        if entry and entry.target.id == user.id:
            msg = f"**{entry.user}** banned **{entry.target}** for: {entry.reason or 'No reason provided'}"
            await self.notify(msg)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await self.get_latest_entry(guild, discord.AuditLogAction.unban)
        if entry and entry.target.id == user.id:
            msg = f"**{entry.user}** unbanned **{entry.target}**"
            await self.notify(msg)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        entry = await self.get_latest_entry(role.guild, discord.AuditLogAction.role_create)
        if entry and entry.target.id == role.id:
            msg = f"➕ **{entry.user}** created role **{role.name}**"
            await self.notify(msg)
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        entry = await self.get_latest_entry(role.guild, discord.AuditLogAction.role_delete)
        if entry and entry.target.id == role.id:
            msg = f"➖ **{entry.user}** deleted role **{role.name}**"
            await self.notify(msg)


async def setup(bot):
    await bot.add_cog(hAudit(bot))