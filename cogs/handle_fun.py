from typing import List
import discord
from discord.ext import commands as dCommands
from interface.interface_json import IF_JSON
import interface.interface_response as uResponse
import util.utils_string as uString
import aimoderator

PATH_RESPONSES = "./__data/responses.json"

class hFun(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @dCommands.hybrid_group(name="fun", with_app_command=True, invoke_without_command=True)
    async def fun(self, ctx):
        RESPONSE, URL = uResponse.getRandom("failedKill")
        await ctx.send(RESPONSE)
        await ctx.defer()

    @fun.command("explode", with_app_command=True, description="Triggers an explosive reaction for fun!")
    async def explode(self, ctx):
        RESPONSE, URL = uResponse.getRandom("explode")
        await ctx.reply(RESPONSE)
        await ctx.defer()

    @fun.command("avatar", with_app_command=True, description="I see you....")
    async def avatar(self, ctx):
        person = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
        
        embed = discord.Embed(
            title=f"{person.name}'s Avatar:",
            color=0xFF5733
        )
        embed.set_image(url=person.avatar.url)
        await ctx.send(embed=embed)
        await ctx.defer()

    @fun.command("gif", with_app_command=True, description="Random gif+response....")
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

    @fun.command("add", with_app_command=True, description="Add prompts or gifs to my database")
    async def add (self, ctx: dCommands.context, key: str, value: str):
        RESPONSES = IF_JSON(path=PATH_RESPONSES)
        STRING = uString.shorten_string(value, 2000)
        RESPONSE, URL = uResponse.getRandom("finishAdd")
        moderator = aimoderator.AIModerator(ctx.guild)
        flagged, aiflagged, response = moderator.scanText(STRING)
        if flagged :
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.mention} Your message has been flagged for poor content and will not be added to my response database.")
            return

        match key:
            case "gif":
                if not value :
                    await ctx.reply("Please provide a gif to add") 
                    return
                try: 
                    RESPONSES.addList(
                        file_path=PATH_RESPONSES,
                        key_path=["random", "_urls"],
                        item=STRING
                        )
                    await ctx.reply(RESPONSE)
                except Exception as e:
                    await ctx.reply(e)
            case "response":
                if not value :
                    await ctx.reply("Please provide a response to add")
                    return
                try:
                    RESPONSES.addList(
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
