import discord
from interface.interface_openai import IF_GPT
from discord.ext import commands as dCommands

class hDirectMessages(dCommands.Cog):
    def __init__(self, bot):
        self.gpt = IF_GPT()
        self.bot = bot

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

        systemPrompt = f"You are talking to: {message.author.name}, you share the following guilds: {message.author.mutual_guilds}"

        try:
            conversation = self.historyToChatStruct(message.channel)
            response = self.gpt.chat(input=conversation, additionalprompt=systemPrompt)
        except Exception as e:
            response = f"Sorry, I had a problem processing your request....\n{e}"
        
        await message.channel.send(response)

async def setup(bot):
    await bot.add_cog((bot))