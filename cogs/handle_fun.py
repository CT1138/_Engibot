import discord
from discord import utils as dUtils
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import util.Response as uResponse
import util.utils_string as uString
import actions

PATH_RESPONSES = "./data/responses.json"

class hFun(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.command("hello", with_app_command=True)
    async def hello(self, ctx):
        await ctx.reply("i know what kind of man you are")
        await ctx.defer()

    @dCommands.command("tf2", with_app_command=True)
    async def tf2(self, ctx, arg1):
        if(arg1 == "") : 
            await ctx.reply("Please provide a class!")
            return
        try:
            CHARACTER = actions.dTF2.TF2Character(arg1)
            EMBED = discord.Embed(
                title=CHARACTER.name,
                description=CHARACTER.description,
                color=0xFF5733
            )
            EMBED.set_image(url=CHARACTER.thumbnail)
            await ctx.reply(embed=EMBED)
        except ValueError as e:
            print(e)
            await ctx.reply("You did not provide a valid class!")
        await ctx.defer()

    @dCommands.command("explode", with_app_command=True)
    async def explode(self, ctx):
        RESPONSE, URL = uResponse.getRandom("explode")
        await ctx.reply(RESPONSE)
        await ctx.defer()

    @dCommands.command("avatar", with_app_command=True)
    async def avatar(self, ctx, args):
        await actions.Avatar.collect(ctx)
        await ctx.defer()

    @dCommands.command("flag", with_app_command=True)
    async def flag (self, ctx, arg1, arg2):
        await actions.Flag.pride(ctx, arg1, arg2)
        await ctx.defer()

    @dCommands.command("gif", with_app_command=True,)
    async def gif (self, ctx: dCommands.Context, index=-1):
        if index == -1 :
            RESPONSE, URL = uResponse.getRandom("random")
        elif index == -2: 
            RESPONSE, URL = uResponse.getLast("random")
        else:
            RESPONSE, URL = uResponse.get("random", aiIndex=index)
        await ctx.send(RESPONSE)
        await ctx.send(URL)
        await ctx.defer()
        

    @dCommands.command("add", with_app_command=True)
    async def add (self, ctx, type:str, content:str):
        print("Called add")
        STRING = uString.shorten_string(content, 2000)
        RESPONSE, URL = uResponse.getRandom("finishAdd")

        match type:
            case "gif":
                if not content :
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
                if not content :
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
