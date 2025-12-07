import discord
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild
import asyncio

class Descriptions:
    SETUP_COLORS = "[STAFF] Initialize color roles in the server."
    LIST_COLORS = "Lists available color roles."
    GET_COLOR = "Assigns you a color role. Usage: get-color <color|hex>"
    REMOVE_COLOR = "Removes your color role."
    CLEANUP_COLORS = "[STAFF] Removes unused color roles from the server."

class Messages:
    START_SETUP = "Setting up color roles, please wait..."
    SETUP_SUCCESS = "Color roles have been set up successfully."
    SETUP_FAILURE = "Failed to set up color roles, something went wrong."
    NOPERMS = "You do not have permission to use this command."
    LIST_COLORS = "**Available color roles:** {role_list} \n You can also provide a hex code (e.g., #FF5733) to get a custom color!"
    BAD_COLOR = "Color '{color}' not found. Use `list-colors` to see available colors or provide a valid hex code."
    FAILED_ROLE = "Failed to create or fetch the color role. Please check my permissions and try again."
    ADDED_ROLE = "You have been assigned the color role: {role_name}"
    REMOVED_ROLE = "Removed color roles: {roles}"
    NO_ROLES_TO_REMOVE = "You do not have any color roles to remove."
    CLEANUP_SUCCESS = "Removed unused color roles: {roles}"
    NO_UNUSED_ROLES = "No unused color roles found."
    REMOVE_CONFIRMATION = "The following unused color roles will be removed:\n{role_names}\n\nType `yes` to confirm, anything else to cancel."
    CLEANUP_CANCELED = "Cleanup canceled."

class Actions:
    class Reasons:
        COLOR_ROLE_SETUP = "Setting up color roles"
        COLOR_ROLE_UPDATE = "Updating color role"
        COLOR_ROLE_ASSIGN = "Assigning color role"
        COLOR_ROLE_POSITION = "Setting up color role position"

class Colors:
    colors = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "yellow": discord.Color.gold(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "pink": discord.Color.magenta(),
            "cyan": discord.Color.teal(),
            "white": discord.Color.light_grey(),
            "black": discord.Color.default()
        }

class hColor(dCommands.Cog):
    def __init__(self, bot: dCommands.Bot):
        self.bot = bot

    # MAKE ROLES AND EVERYTHING
    @dCommands.command(name="setup-colors", help=Descriptions.SETUP_COLORS)
    async def setupcolors(self, ctx: dCommands.Context):
        iGuild = IF_Guild(ctx.guild)
        await iGuild.initialize()

        if iGuild.isStaff(ctx.author.id):
            await ctx.send(Messages.START_SETUP)
            setup = await self.initcolors(iGuild)
            if setup == 0:
                await ctx.send(Messages.SETUP_SUCCESS)
            else:
                await ctx.send(Messages.SETUP_FAILURE)
        else:
            await ctx.send(Messages.NOPERMS)

    async def initcolors(self, iGuild: IF_Guild = None):
        guild = iGuild.guild if iGuild else None
        if guild is None: return 1

        if not guild.me.guild_permissions.manage_roles:
            return 1
        
        for role in guild.roles:
            if role.name.lower() in Colors.colors or role.name.startswith("color-"):
                await self.positionRole(iGuild, role)
    
        for color in Colors.colors:
            role_name = f"{color.capitalize()}"
            role_color = Colors.colors[color]
            await self.createRole(iGuild, role_name, role_color)

        return 0
    
    async def positionRole(self, iGuild: IF_Guild, role: discord.Role):
        guild = iGuild.guild

        base_role = iGuild.getRoleByType("member")
        role_position = base_role.position + 1 if base_role else len(guild.roles) - 1
        bot_top_role = guild.me.top_role
        if role_position >= bot_top_role.position:
            role_position = bot_top_role.position - 1

        await guild.edit_role_positions(positions={role: role_position}, reason=Actions.Reasons.COLOR_ROLE_POSITION)


    async def createRole(self, iGuild: IF_Guild, name: str, color: discord.Color, *args, **kwargs):
        guild = iGuild.guild
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            role = await guild.create_role(name=name)

        role_color = color or discord.Color.default()
        base_role = iGuild.getRoleByType("member")

        role_position = base_role.position + 1 if base_role else len(guild.roles) - 1
        bot_top_role = guild.me.top_role
        if role_position >= bot_top_role.position:
            role_position = bot_top_role.position - 1

        await role.edit(color=role_color, reason=Actions.Reasons.COLOR_ROLE_UPDATE)
        await guild.edit_role_positions(positions={role: role_position})

        return role

    @dCommands.command(name="list-colors", help=Descriptions.LIST_COLORS)
    async def listcolors(self, ctx: dCommands.Context):
        role_list = ", ".join([color.capitalize() for color in Colors.colors.keys()])
        await ctx.send(Messages.LIST_COLORS.format(role_list=role_list))

    @dCommands.command(name="get-color", help=Descriptions.GET_COLOR)
    async def getcolor(self, ctx: dCommands.Context, color: str):
        member = ctx.author
        iGuild = IF_Guild(ctx.guild)
        await iGuild.initialize()

        color_lower = color.lower()

        if color_lower in Colors.colors:
            # Determined as color
            role_color = Colors.colors[color_lower]
            role_name = color_lower.capitalize()
        else:
            # Try it as a hex
            try:
                role_color = discord.Color.from_str(color)
            except ValueError:
                await ctx.send(Messages.BAD_COLOR.format(color=color))
                return

            # For hex codes, use "color-<HEX>" as role name
            role_name = f"color-{color.lstrip('#').upper()}"

        # Create or move the role using your function
        role = await self.createRole(iGuild, role_name, role_color)

        if role is None:
            await ctx.send(Messages.FAILED_ROLE)
            return

        # Remove existing color roles from member
        for existing_role in member.roles:
            if existing_role.name.lower() in Colors.colors or existing_role.name.startswith("color-"):
                await member.remove_roles(existing_role, reason=Actions.Reasons.COLOR_ROLE_ASSIGN)

        # Assign the new role
        await member.add_roles(role, reason=Actions.Reasons.COLOR_ROLE_ASSIGN)
        await ctx.send(Messages.ADDED_ROLE.format(role_name=role_name))

    @dCommands.command(name="remove-color", help=Descriptions.REMOVE_COLOR)
    async def removecolor(self, ctx: dCommands.Context):
        member = ctx.author

        # Remove existing color roles
        removed_roles = []

        for existing_role in member.roles:
            if existing_role.name.lower() in self.colors or existing_role.name.startswith("color-"):
                await member.remove_roles(existing_role, reason=Actions.Reasons.COLOR_ROLE_ASSIGN)
                removed_roles.append(existing_role.name)

        if removed_roles:
            await ctx.send(Messages.REMOVED_ROLE.format(roles=", ".join(removed_roles)))
        else:
            await ctx.send(Messages.NO_ROLES_TO_REMOVE)

    @dCommands.command(name="cleanup-colors", help=Descriptions.CLEANUP_COLORS)
    async def cleanup_colors(self, ctx: dCommands.Context):
        iGuild = IF_Guild(ctx.guild)
        await iGuild.initialize()
        if not iGuild.isStaff(ctx.author.id):
            await ctx.send(Messages.NOPERMS)
            return
        
        guild = ctx.guild
        unused_roles = []

        # Collect all unused hex color roles
        for role in guild.roles:
            if role.name.startswith("color-") and len(role.members) == 0:
                unused_roles.append(role)

        if not unused_roles:
            await ctx.send(Messages.NO_UNUSED_ROLES)
            return

        # List the roles and ask for confirmation
        role_names = ", ".join([role.name for role in unused_roles])
        prompt = await ctx.send(Messages.REMOVE_CONFIRMATION.format(roles=role_names))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            confirmation = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(Messages.CLEANUP_CANCELED)
            return

        if confirmation.content.lower() != "yes":
            await ctx.send(Messages.CLEANUP_CANCELED)
            return

        # Delete the roles
        removed_names = []
        for role in unused_roles:
            await role.delete(reason=Actions.Reasons.COLOR_ROLE_ASSIGN)
            removed_names.append(role.name)
        if removed_names:
            await ctx.send(Messages.REMOVED_ROLE.format(roles=", ".join(removed_names)))
        else:
            await ctx.send(Messages.NO_UNUSED_ROLES)

async def setup(bot):
    await bot.add_cog(hColor(bot))