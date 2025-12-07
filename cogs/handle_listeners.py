import discord
import re
import util.utils_math as uMath
from discord.ext import commands as dCommands
from interface.interface_guild import IF_Guild, ChannelType
from sql.SQLCommands import SQLCommands
from interface.interface_database import IF_Database
from interface.interface_response import IF_Response, ResultType
from interface.interface_openai import AIChatbot
import math
from datetime import datetime, timedelta

class hListener(dCommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RESPONSE = IF_Response()
        self.cooldowns = {}
        self.cooldown = 10

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild: return
        GUILD = IF_Guild(message.channel.guild)
        await GUILD.initialize()
        CHANNELTYPE = GUILD.getChannelType(message.channel.id)

        DB = IF_Database()
        await DB.connect()

        params = (
            message.id,
            message.guild.id if message.guild else None,
            message.guild.name if message.guild else None,
            message.channel.id,
            message.channel.name,
            message.author.id,
            message.author.name,
            message.content,
            message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        )
        DB.query(SQLCommands.INSERT_MESSAGE.value, params)

        # Do not do anything if :
        ##if message.author.bot : return # author is a bot (icky who would want to be a bot?)
        ##if message.author.id == self.bot.user.id : return # message is from the bot itself

        url_pattern = re.compile(r"https?://(?:www\.)?tenor\.com[^\s]*")
        if url_pattern.search(message.content) and not message.author.id == self.bot.user.id:
            link = re.findall(url_pattern, message.content)[0]
            await self.RESPONSE.add("random", link, result_type=ResultType.URL)
            print(f"[RESPONSE] scalped and found gif {link}")

        #if GUILD.Config["chatcompletions"]:
        #    Chatterbox = AIChatbot(f"You are an observer of a discord conversation in a server called {GUILD.guildName}")
        #    Context = await Chatterbox.channelToGPT(message.channel)
        #    Completion = Chatterbox.chatCompletion(Context)
        #    print("[AI] " + Completion)

        ############################
        # Cooldown to avoid spamming
        ############################
        now = datetime.now()
        user_id = message.author.id
        cooldown_time = timedelta(minutes=self.cooldown)
        
        last = self.cooldowns.get(user_id)
        if last and (now - last) < cooldown_time:
            print(f"A message was sent, but I am currently under cooldown for: {now - last}/{cooldown_time}")
            return

        # Starboard features
        if message.attachments:
            if CHANNELTYPE == ChannelType.ART:
                await message.add_reaction("<:happi:1355706814083371199>")

        # Random Reactions / Responses
        if not CHANNELTYPE == ChannelType.SILLY:
            DB.__del__()
            return
        
        if uMath.roll(100 - 0.5, "lol"):
            emojis = ["😂", "🤣", "😆", "😹", "🫃", "<:4devious_dimple:1433658007463399445>", "<:peak:1437901360430448762>", "<:3tennadoom:1401737657947783259>", "<:4freak_spotted:1391194805928853545>"]
            emoji = uMath.randElement(emojis)
            await message.add_reaction(emoji)
            self.cooldowns[user_id] = now

        CHANCE = GUILD.getChance("Response")
        if uMath.roll(CHANCE, "Response"):
            RESPONSE = await self.RESPONSE.getRandom("random" , result_type=ResultType.RESPONSE)
            URL = await self.RESPONSE.getRandom("random", result_type=ResultType.URL)
            self.cooldowns[user_id] = now
            print("Sending a random response")
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

        DB.__del__()

async def setup(bot):
    await bot.add_cog(hListener(bot))
