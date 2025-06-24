from typing import List
import discord
from discord.ext import commands as dCommands
from interface.interface_json import IF_JSON
from interface.interface_response import IF_Response
import util.utils_string as uString
import aimoderator

class hFun(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response = IF_Response()

    @dCommands.hybrid_group(name="fun", with_app_command=True, invoke_without_command=True)
    async def fun(self, ctx):
        RESPONSE, URL = await self.response.getRandom("failedKill")
        await ctx.send(RESPONSE)
        await ctx.defer()

    @fun.command("explode", with_app_command=True, description="Triggers an explosive reaction for fun!")
    async def explode(self, ctx):
        RESPONSE, URL = await self.response.getRandom("explode")
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
            RESPONSE, URL = await self.response.getRandom("random")
        elif index == -2: 
            RESPONSE, URL = await self.response.getLast("random")
        else:
            RESPONSE, URL = await self.response.get("random", aiIndex=index)

        await ctx.message.channel.send(RESPONSE)
        await ctx.message.channel.send(URL)
        await ctx.defer()

    @fun.command("add", with_app_command=True, description="Add prompts or gifs to my database")
    async def add (self, ctx: dCommands.context, key: str, value: str):
        STRING = uString.shorten_string(value, 2000)
        RESPONSE, URL = await self.response.getRandom("finishAdd")
        moderator = aimoderator.AIModerator(ctx.guild)
        await moderator.initialize()
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
                    await self.response.add(
                        key="random",
                        phrase=STRING
                        )
                    await ctx.reply(RESPONSE)
                except Exception as e:
                    await ctx.reply(e)
            case "response":
                if not value :
                    await ctx.reply("Please provide a response to add")
                    return
                try:
                    await self.response.add(
                        key="random",
                        phrase=STRING
                        )
                    await ctx.reply(RESPONSE)
                except Exception as e:
                    await ctx.reply(e)
        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hFun(bot))
