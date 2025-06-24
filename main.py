import os
import discord
from discord.ext import commands as dCommands
from interface.interface_json import IF_JSON
from interface.interface_guild import IF_Guild

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
    print(f'[BOT] Logged in as {bot.user} (ID: {bot.user.id})')

    for guild in bot.guilds:
        G = IF_Guild(guild)
        await G.initialize()
    
    # TODO: Add cycling status option (eg chance every 30 minutes or hour)
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name=STATUS)
    )

# RUN
bot.run(TOKENS.json["botToken"])