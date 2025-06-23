from discord.ext import commands as dCommands
import interface.interface_response as uResponse
from interface.interface_json import IF_JSON
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

    @util.command("ignore", with_app_command=True, description="Do you wish to withdraw from my interaction system")
    async def ignoreme(self, ctx, ignore:bool):
        IGNORES = IF_JSON(path=PATH_IGNORES)
        ID = ctx.author.id
        RESPONSE = uResponse.getRandom("!placeholder")
        if ignore :
            RESPONSE, URL = uResponse.getRandom("ignore")
            IGNORES.addList(
                file_path=PATH_IGNORES,
                key_path=["members"],
                item=ID
            )
        elif not ignore :
            RESPONSE, URL = uResponse.getRandom("unIgnore")
            IGNORES.removeList(
                file_path=PATH_IGNORES,
                key_path=["members"],
                item=ID
            )
        await ctx.reply(RESPONSE)
        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hUtil(bot))
