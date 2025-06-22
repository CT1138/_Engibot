from discord.ext import commands as dCommands
import util.utils_json as ujReader
import actions.Response as uResponse
import util.utils_string as uString
import actions
import aimoderator

PATH_RESPONSES = "./__data/responses.json"
moderator = aimoderator.AIModerator()

class hFun(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.hybrid_group(name="fun", with_app_command=True, invoke_without_command=True)
    async def fun(self, ctx):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        await ctx.send(RESPONSE)
        await ctx.defer()

    @fun.command("hello", with_app_command=True)
    async def hello(self, ctx):
        await ctx.reply("i know what kind of man you are")
        await ctx.defer()

    @fun.command("explode", with_app_command=True)
    async def explode(self, ctx):
        RESPONSE, URL = uResponse.getRandom("explode")
        await ctx.reply(RESPONSE)
        await ctx.defer()

    @fun.command("avatar", with_app_command=True)
    async def avatar(self, ctx, args):
        await actions.Avatar.collect(ctx)
        await ctx.defer()

    @fun.command("flag", with_app_command=True)
    async def flag (self, ctx, arg1, arg2):
        await actions.Flag.pride(ctx, arg1, arg2)
        await ctx.defer()

    @fun.command("gif", with_app_command=True,)
    async def gif (self, ctx: dCommands.Context, index=-1):
        if index == -1 :
            RESPONSE, URL = uResponse.getRandom("random")
        elif index == -2: 
            RESPONSE, URL = uResponse.getLast("random")
        else:
            RESPONSE, URL = uResponse.get("random", aiIndex=index)

        await ctx.message.channel.send(RESPONSE)
        await ctx.message.channel.send(URL)
        await ctx.defer()
        

    @fun.command("add", with_app_command=True)
    async def add (self, ctx, object: str, element: str):
        print("Called add")
        STRING = uString.shorten_string(element, 2000)
        RESPONSE, URL = uResponse.getRandom("finishAdd")
        flagged, aiflagged, response = moderator.scanText(STRING)

        if flagged :
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.mention} Your message has been flagged for poor content and will not be added to my response database.")
            return

        match object:
            case "gif":
                if not element :
                    await ctx.reply("Please provide a gif to add") 
                    return
                try: 
                    ujReader.addList(
                        file_path=PATH_RESPONSES,
                        key_path=["random", "_urls"],
                        item=STRING
                        )
                    await ctx.reply(RESPONSE)
                except Exception as e:
                    await ctx.reply(e)
            case "response":
                if not element :
                    await ctx.reply("Please provide a response to add")
                    return
                try:
                    ujReader.addList(
                        file_path=PATH_RESPONSES,
                        key_path=["random", "_responses"],
                        item=STRING
                    )
                    await ctx.reply(RESPONSE)
                except Exception as e:
                    await ctx.reply(e)
        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hFun(bot))
