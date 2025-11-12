import discord
from discord.ext import commands
from sql.SQLCommands import SQLCommands
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_response import IF_Response, ResultType

class hQuotebook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response = IF_Response()

    @commands.command("quotebook", with_app_command=True, description="Get a random quote from the book of quotes")
    async def quotebook(self, ctx: commands.Context):
        quote = await self.response.getRandom(key=ctx.guild.name, result_type=ResultType.QUOTEBOOK)
        if quote:
            await ctx.send(quote)
        else:
            await ctx.send("No quotes found! Better get to work!")
        await ctx.defer()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.upload_quotebook_messages(message.guild, limit=10)

    async def upload_quotebook_messages(self, guild: discord.Guild, limit=100):
        interface_guild = IF_Guild(guild)
        await interface_guild.initialize()

        quotebook_channel = await interface_guild.getChannelByType(ChannelType.QUOTEBOOK)
        if quotebook_channel is None:
            print("Quotebook channel not found")
            return

        print(f"Found quotebook channel: {quotebook_channel.name}")

        messages = await quotebook_channel.history(limit).flatten()

        for msg in messages:
            image_url = None
            if msg.attachments:
                for att in msg.attachments:
                    if att.content_type and att.content_type.startswith("image"):
                        image_url = att.url
                        break
            if not image_url and msg.embeds:
                for embed in msg.embeds:
                    if embed.image and embed.image.url:
                        image_url = embed.image.url
                        break

            # Check if message starts with a quote
            starts_with_quote = msg.content.startswith('"') if msg.content else False

            if image_url or starts_with_quote:
                content_to_upload = image_url if image_url else msg.content
                print(f"Uploading: {content_to_upload}")
                try:
                    await interface_guild.db.query(
                        SQLCommands.INSERT_QUOTEBOOK,
                        (msg.id, interface_guild.guildID, interface_guild.guildName,
                        msg.channel.id, msg.channel.name, msg.author.id,
                        msg.author.name, content_to_upload, msg.created_at)
                    )
                except Exception as e:
                    print(f"Error uploading message {msg.id}: {e}")

async def setup(bot):
    await bot.add_cog(hQuotebook(bot))