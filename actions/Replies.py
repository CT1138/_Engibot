import discord
from util import utils_math as uMath
from util import utils_json as jReader
from actions import Response

CHANNELS = jReader.read("./__data/channels.json")

async def reply_random(message, abForce=False):
    RESPONSE, URL = Response.getRandom("random")
    CHANCE = 95
    if(abForce) : CHANCE = 0

    if message.channel.id in CHANNELS["silly"]:
        if uMath.roll(CHANCE, "Response"):
            if(uMath.roll(80, "Send All")):
                # 20% Chance to send RESPONSE & URL
                await message.channel.send(RESPONSE)
                await message.channel.send(URL)
            else:
                # 80% Chance to only send GIF or RESPONSE
                if(uMath.roll(50, "Send Gif or Response")) :    
                    await message.channel.send(URL)
                else:                               
                    await message.channel.send(RESPONSE)

async def reply_bro(message: discord.Message, abForce=False, aiChance=70):
    # Amayah
    if message.author.id == 1058073516186026095 : aiChance = aiChance - 30
    # June
    if message.author.id == 752989978535002134 : aiChance = 10
    # If forced
    if abForce : aiChance = 0

    if uMath.roll(aiChance, "Bro Went") : return
    if not message.channel.id in CHANNELS["silly"]: 
        if abForce : await message.reply("I'm not meant to be silly here </3")
        return

    HASACTION = False
    ACTION = ""
    KEYWORDS = [
        "so i",
        "and i",
        "then i",
        "until i"
    ]

    PATH = "./__data/assets/bro.jpg"
    with open(PATH, 'rb') as f:
        IMG = discord.File(f)

    for key in KEYWORDS:
        if key in message.content.lower():
            HASACTION = True
            PARTS = message.content.split(key, 1)
            ACTION = PARTS[1].strip()
    if HASACTION : 
        await message.channel.send(content=f"Bro {ACTION}", file=IMG)