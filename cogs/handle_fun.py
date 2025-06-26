import discord
from discord.ext import commands as dCommands
from interface.interface_database import IF_Database
from interface.interface_response import IF_Response, ResultType
import util.utils_string as uString
import random

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
        quote = await self.response.getRandom(key=ctx.guild.name, result_type=ResultType.QUOTEBOOK)
        if quote:
            await ctx.send(quote)
        else:
            await ctx.send("No quotes found! Better get to work!")
        await ctx.defer()

    @fun.command("memory", with_app_command=True, description="Get a random memory")
    async def memory(self, ctx: dCommands.Context):
        memory = await self.response.getRandom(key=ctx.guild.name, result_type=ResultType.MEMORY)
        print(f"[MEMORY] {memory}")
        if memory:
            await ctx.send(memory)
        else:
            await ctx.send("No memories found! Quit slacking!")
        await ctx.defer()

    @fun.command("collection", with_app_command=True, description="View a random image from a collection")
    async def collection(self, ctx: dCommands.Context, collection: str = None, index: int = -1):
        db = IF_Database()
        await db.connect()

        if not collection:
            collections = db.getCollections(ctx.guild.id)
            await ctx.send(f"Please specify a collection name. Available collections: {', '.join(collections)}")
            return

        images = db.getImagesByCollection(ctx.guild.id, collection)
        if not images:
            await ctx.send(f"No images found in the `{collection}` collection. Either create one or add images to it.")
            return

        if index == -1:
            image = images[random.randint(0, len(images) - 1)]
        else:
            image = images[index]

        with open(image['filepath'], 'rb') as f:
            file = discord.File(f, filename=image['filepath'].split('/')[-1])
            await ctx.send(file=file)

    @fun.command("add-to-collection", description="Upload one or more images to a collection")
    async def add_to_collection(self, ctx: dCommands.Context, collection: str = None):
        db = IF_Database()
        await db.connect()

        if not collection:
            collections = db.getCollections(ctx.guild.id)
            await ctx.send(f"Please specify a collection name.\nAvailable collections: {', '.join(collections)}")
            return

        if not ctx.message.attachments:
            await ctx.send("Please attach at least one image.")
            return

        success_count = 0
        failed_files = []

        for attachment in ctx.message.attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                failed_files.append(attachment.filename)
                continue

            try:
                await db.addImage(
                    attachment,
                    guild_id=ctx.guild.id,
                    author_id=ctx.author.id,
                    collection=collection
                )
                success_count += 1
            except Exception as e:
                print(f"[Collection] Failed to save image: {e}")
                failed_files.append(attachment.filename)

        # Build response
        messages = []
        if success_count:
            messages.append(f"Successfully added {success_count} image(s) to `{collection}`.")
        if failed_files:
            messages.append(f"Skipped unsupported or failed files: {', '.join(failed_files)}")

        await ctx.send("\n".join(messages))

    @fun.command("add", with_app_command=True, description="Add prompts, gifs, quotes, or memories to my database")
    async def add(self, ctx: dCommands.context, key="", value=""):
        STRING = uString.shorten_string(value, 2000)
        RESPONSE = await self.response.getRandom("finishAdd", result_type=ResultType.RESPONSE)
        DATABASEKEY = "random"

        if not key or not value:
            await ctx.reply("Please provide both a key and a value to add... valied keys: response, gif, memory, quotebook")
            return

        # Validate ResultType
        try:
            result_type = ResultType[key.upper()]
        except KeyError:
            await ctx.reply("Invalid type. Choose from: response, gif, memory, quotebook")
            return

        # Validate content
        if not value:
            await ctx.reply("Please provide a value to add.")
            return
        
        if result_type == ResultType.MEMORY or result_type == ResultType.QUOTEBOOK:
            if not ctx.guild:
                await ctx.reply("This command can only be used in a server.")
                return
            DATABASEKEY = ctx.guild.name

        try:
            await self.response.add(
                key=DATABASEKEY,
                phrase=STRING,
                result_type=result_type,
            )
            await ctx.reply(RESPONSE)
        except Exception as e:
            await ctx.reply(f"Error: {str(e)}")

        await ctx.defer()

async def setup(bot):
    await bot.add_cog(hFun(bot))
