import os
import sys
import discord
from discord import utils as dUtils, File, app_commands
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import actions.Response as uResponse

CONFIG = ujReader.read("./__data/config.json")
# VARIABLES
STARBOARD_EMOJI = CONFIG["emojis"]["starboard"]
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]

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

    # Pure slash command: kill
    @app_commands.command(name="kill", description="Shut down the bot")
    async def kill(self, interaction: discord.Interaction):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        role = dUtils.get(interaction.guild.roles, id=STAFF)
        if role in interaction.user.roles:
            await interaction.response.send_message("Shutting down...", ephemeral=True)
            await self.bot.close()
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)

    # Pure slash command: restart
    @app_commands.command(name="restart", description="Restart the bot")
    async def restart(self, interaction: discord.Interaction):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        role = dUtils.get(interaction.guild.roles, id=STAFF)
        if role in interaction.user.roles:
            await interaction.response.send_message("Restarting...", ephemeral=True)
            await self.bot.close()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            await interaction.response.send_message(RESPONSE, ephemeral=True)

    # Pure slash command: check_role
    @app_commands.command(name="check_role", description="Check if a member has a given role ID")
    @app_commands.describe(member="The member to check", role_id="The ID of the role to check")
    async def check_role(self, interaction: discord.Interaction, member: discord.Member, role_id: int):
        role = dUtils.get(interaction.guild.roles, id=role_id)
        if role is None:
            await interaction.response.send_message(f"Role with ID {role_id} not found.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message(f"{member.display_name} has the role: {role.name}", ephemeral=True)
        else:
            await interaction.response.send_message(f"{member.display_name} does not have the role: {role.name}", ephemeral=True)

    # Pure slash command: dump
    @app_commands.command(name="dump", description="Dump a JSON file to HTML")
    @app_commands.describe(choice="The JSON file to dump (no extension)")
    async def dump(self, interaction: discord.Interaction, choice: str):
        await interaction.response.defer(ephemeral=False)
        json_path = f"./__data/{choice}.json"
        try:
            dump_path = ujReader.dumpHTML(json_path)  # returns .html file path
            await interaction.followup.send(
                content=f"Here's the HTML dump for `{choice}.json`:",
                file=File(dump_path)
            )
        except FileNotFoundError:
            await interaction.followup.send(f"❌ File `{choice}.json` not found.")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {e}")

    # Autocomplete handler for dump
    @dump.autocomplete("choice")
    async def dump_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=name, value=name)
            for name in self.get_json_choices()
            if current.lower() in name.lower()
        ]

async def setup(bot):
    await bot.add_cog(hStaff(bot))
