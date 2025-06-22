import discord
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import actions.Response as uResponse
import util.utils_discord as uDiscord

# VARIABLES
PATH_IGNORES = "./__data/ignores.json"

class hUtil(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.hybrid_group(name="util", with_app_command=True, invoke_without_command=True)
    async def util(self, ctx):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        await ctx.send(RESPONSE)
        await ctx.defer()

    @util.command("personal", with_app_command=True)
    async def ignoreme(self, ctx, ignore:bool):
        ID = ctx.author.id
        RESPONSE = uResponse.getRandom("!placeholder")
        if ignore :
            RESPONSE, URL = uResponse.getRandom("ignore")
            ujReader.addList(
                file_path=PATH_IGNORES,
                key_path=["members"],
                item=ID
            )
        elif not ignore :
            RESPONSE, URL = uResponse.getRandom("unIgnore")
            ujReader.removeList(
                file_path=PATH_IGNORES,
                key_path=["members"],
                item=ID
            )
        await ctx.reply(RESPONSE)
        await ctx.defer()

    @util.command("commands", with_app_command=True)
    async def commands(self, ctx):
        EMBED : discord.Embed = uDiscord.help()
        await ctx.channel.send(embed=EMBED)
        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hUtil(bot))
