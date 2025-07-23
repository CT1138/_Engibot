import os
import discord
import asyncio
from discord.ext import commands as dCommands
from interface.interface_ntfy import IF_NTFY
from interface.interface_json import IF_JSON
from interface.interface_guild import IF_Guild, ChannelType
from interface.interface_database import IF_Database, SQLCommands
from interface.interface_backend import IF_Backend

# Data
CONFIG = IF_JSON("./__data/config.json")
TOKENS = IF_JSON("./__data/tokens.json")

# VARIABLES
PREFIX = "-"
STATUS = CONFIG.json["status"]

# Setup Bot
MYINTENTS = discord.Intents.all()
MYINTENTS.reactions = True
bot = dCommands.Bot(command_prefix=PREFIX, intents=MYINTENTS)

# EVENTS
@bot.event
async def on_ready():
    # Load Cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"[COG] Loading cog {filename}")
            await bot.load_extension(f"cogs.{filename[:-3]}")
    try:
        synced = await bot.tree.sync()
        print(f"[COG] Synced {len(synced)} application commands.")
    except Exception as e:
        print(f"[COG] Sync failed: {e}")

    # After general bot setup
    login_message = f'[BOT] Logged in as {bot.user} (ID: {bot.user.id})'
    print(login_message)
    notification = IF_NTFY()
    notification.post(msg=login_message)

    for guild in bot.guilds:
        G = IF_Guild(guild)
        await G.initialize()
    
    # TODO: Add cycling status option (eg chance every 30 minutes or hour)
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name=STATUS)
    )

async def upload_quotebook_messages(bot, guild: discord.Guild, limit=100):
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

backend = IF_Backend(bot)
backend.start_in_background()

# RUN
bot.run(TOKENS.json["botToken"])