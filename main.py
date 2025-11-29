#!/usr/bin/env python3
import os, discord
from discord.ext import commands
from interface.interface_database import IF_Database

# Setup Bot
intents = discord.Intents.all()
prefix = os.getenv("BOT_PREFIX") or "!"
status = os.getenv("BOT_STATUS") or "Goon or be Gooned"
bot = commands.Bot(command_prefix=prefix, intents=intents)

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
    # Attempt Database Connection
    db = IF_Database()
    if await db.connect(): print("[BOT] First time connection to database, success.")
    else: print("[BOT] Couldn't connect to Database!")
    
    # TODO: Add cycling status option (eg chance every 30 minutes or hour)
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name=status)
    )

# RUN
token = os.getenv("DISCORD_TOKEN")
if not token: raise ValueError
bot.run(token)