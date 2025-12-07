import discord, dotenv, os
from interface.interface_openai import IF_GPT
from discord.ext import commands as dCommands
from datetime import datetime, timedelta

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH") or 2000)

class hDirectMessages(dCommands.Cog):
    def __init__(self, bot):
        self.gpt = IF_GPT()
        self.bot = bot

    def split_message(self, text, max_length=MAX_MESSAGE_LENGTH):
        chunks = []
        while len(text) > max_length:
            split_at = text.rfind('\n', 0, max_length) 
            if split_at == -1:
                split_at = max_length 
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip('\n') 
        if text:
            chunks.append(text)
        return chunks

    async def historyToChatStruct(self, channel, limit=100):
        messages = []
        async for message in channel.history(limit=limit, oldest_first=True):
            if message.author.bot and message.author != self.bot.user:
                continue
            
            role = "user" if message.author != self.bot.user else "assistant"
            messages.append({"role": role, "content": message.content})
        return messages

    @dCommands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user: return
        if not message.author.id == 752989978535002134: return
        if message.author.bot: return

        if not isinstance(message.channel, discord.DMChannel): return

        systemPrompt = f"You are talking to: {message.author.name}, you share the following guilds: {message.author.mutual_guilds}."

        try:
            async with message.channel.typing():
                conversation = await self.historyToChatStruct(message.channel)
                response = await self.gpt.chat(input=conversation, additionalprompt=systemPrompt)
        except Exception as e:
            response = f"Sorry, I had a problem processing your request....\n{e}"
        for chunk in self.split_message(response):
            await message.channel.send(chunk)

async def setup(bot):
    await bot.add_cog(hDirectMessages(bot))