import os
import discord
from discord.ext import commands as dCommands
import util.utils_json as ujReader
import util.utils_cache as uCache
import actions.Starboard as uStarboard
import mariadb

# Data
uCache.starboard_load()
CONFIG = ujReader.read("./__data/config.json")
TOKENS = ujReader.read("./__data/tokens.json")
DBLOGIN = TOKENS["mariadb"]

# VARIABLES
PREFIX = CONFIG["prefix"]
STAFF = CONFIG["roles"]["staff"]
STATUS = CONFIG["status"]

# Setup Bot
MYINTENTS = discord.Intents.all()
MYINTENTS.reactions = True
bot = dCommands.Bot(command_prefix=PREFIX, intents=MYINTENTS)

# Define Database
db = mariadb.MariaDBInterface(
    host=DBLOGIN["host"],
    user= DBLOGIN["user"],
    password=DBLOGIN["password"],
    database=DBLOGIN["database"]
)

# EVENTS
@bot.event
async def on_ready():
    # Connect to database, print result
    # print( db.connect() )

    # Load Cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application commands.")
    except Exception as e:
        print(f"Sync failed: {e}")
    
    # After general bot setup
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    # TODO: Add cycling status option (eg chance every 30 minutes or hour)
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name=STATUS)
    )
    await uStarboard._starboard_cache(bot)

# RUN
bot.run(TOKENS["botToken"])