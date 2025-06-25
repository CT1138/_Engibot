import discord
from discord.ext import commands as dCommands
from interface.interface_response import IF_Response, ResultType
import util.utils_string as uString
import aimoderator

class hFun(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response = IF_Response()

    @dCommands.hybrid_group(name="fun", with_app_command=True, invoke_without_command=True)
    async def fun(self, ctx):
        RESPONSE = await self.response.getRandom("failedKill", result_type=ResultType.RESPONSE)
        await ctx.send(RESPONSE)
        await ctx.defer()

    @fun.command("explode", with_app_command=True, description="Triggers an explosive reaction for fun!")
    async def explode(self, ctx):
        RESPONSE = await self.response.getRandom("explode", result_type=ResultType.RESPONSE)
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
            RESPONSE = await self.response.getRandom("random", result_type=ResultType.RESPONSE)
            URL = await self.response.getRandom("random", result_type=ResultType.URL)
        elif index == -2: 
            RESPONSE = await self.response.getLast("random", result_type=ResultType.RESPONSE)
            URL = await self.response.getLast("random", result_type=ResultType.URL)
        else:
            RESPONSE = await self.response.get("random", aiIndex=index, result_type=ResultType.RESPONSE)
            URL = await self.response.get("random", aiIndex=index, result_type=ResultType.URL)

        await ctx.message.channel.send(RESPONSE)
        await ctx.message.channel.send(URL)
        await ctx.defer()

    @fun.command("quotebook", with_app_command=True, description="Get a random quote from the book of quotes")
    async def quotebook(self, ctx: dCommands.Context):
        quote = await self.response.getRandom(key=ctx.guild.name, param="!placeholder", result_type=ResultType.QUOTEBOOK)
        if quote:
            await ctx.send(quote)
        else:
            await ctx.send("No quotes found! Better get to work!")
        await ctx.defer()

    @fun.command("memory", with_app_command=True, description="Get a random memory")
    async def memory(self, ctx: dCommands.Context):
        memory = await self.response.getRandom(key=ctx.guild.name, param="!placeholder", result_type=ResultType.MEMORY)
        if memory:
            await ctx.send(memory)
        else:
            await ctx.send("No memories found! Quit slacking!")
        await ctx.defer()

    @fun.command("add", with_app_command=True, description="Add prompts, gifs, quotes, or memories to my database")
    async def add(self, ctx: dCommands.context, key="", value="", param: str = ""):
        STRING = uString.shorten_string(value, 2000)
        RESPONSE = await self.response.getRandom("finishAdd", result_type=ResultType.RESPONSE)

        if not key or not value:
            await ctx.reply("Please provide both a key and a value to add... valied keys: response, gif, memory, quotebook")
            return

        # Validate ResultType
        try:
            result_type = ResultType[key.upper()]
        except KeyError:
            await ctx.reply("Invalid type. Choose from: response, gif, memory, quotebook")
            return

        # Moderation check in case the user is naughty
        if result_type in {ResultType.RESPONSE, ResultType.MEMORY, ResultType.QUOTEBOOK}:
            moderator = aimoderator.AIModerator(ctx.guild)
            await moderator.initialize()
            flagged, aiflagged, moderation_response = moderator.scanText(STRING)

            if flagged:
                await ctx.message.delete()
                await ctx.send(f"{ctx.author.mention} Your message was flagged and won't be added to my database.")
                return

        # Validate content
        if not value:
            await ctx.reply("Please provide a value to add.")
            return

        try:
            await self.response.add(
                key="random",
                phrase=STRING,
                result_type=result_type,
                param=param
            )
            await ctx.reply(RESPONSE)
        except Exception as e:
            await ctx.reply(f"Error: {str(e)}")

        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hFun(bot))
