from openai import OpenAI
from interface.interface_json import IF_JSON
from interface.interface_guild import IF_Guild
import discord

TOKENS = IF_JSON("./__data/tokens.json").json
client = OpenAI(api_key=TOKENS["openai"])

modModel = "omni-moderation-latest"

class AIModerator:
    def __init__(self, guild: discord.Guild):
        self.GUILD = IF_Guild(guild)
        self.categories_to_flag = self.GUILD.guildConfig["sensitive-content"]
        return
    
    def shouldFlag(self, response):
        result = response.results[0]

        flagged_categories = result.categories.model_dump()

        for category in self.categories_to_flag:
            if flagged_categories.get(category, False):
                return True
        return False

    def scanText(self, prompt):
        response = client.moderations.create(
            model=modModel,
            input=prompt
        )
        flagged = self.shouldFlag(response)
        aiflagged = response.results[0].flagged
        print(f"[AI Mod] Scanned text: {prompt}\n[AI Mod] Flag Decision: {aiflagged}\n[AI Mod] Tuned Flags: {flagged}")
        return flagged, aiflagged, response
    
    def scanImage(self, url):
        response = client.moderations.create(
            model=modModel,
            input=
            [{
                "type": "image_url",
                "image_url": { "url": url, }
            }]
        )
        flagged = self.shouldFlag(response)
        return flagged, response

# It's very unlikely I will implement this as a key feature, but for the sake of curiosity and testing purposes....
class AIChatbot:
    def __init__(self, systemPrompt):
        self.SYSTEMPROMPT = {"role": "system", "content": systemPrompt}
        pass

    def chatCompletion(self, data: dict):
        completion = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=data
        )
        return completion.choices[0].message.content

    async def channelToGPT(self, channel: discord.TextChannel, limit: int = 20) -> list[dict]:
        messages = []
        
        async for msg in channel.history(limit=limit, oldest_first=True):
            # Ignore system messages or webhooks
            if msg.webhook_id or msg.type != discord.MessageType.default:
                continue

            # Skip bot messages unless you want to preserve them
            if msg.author.bot:
                continue

            role = "user"
            content = f"{msg.author.display_name}: {msg.content.strip()}"

            # Only add if the message has content
            if content.strip():
                messages.append({"role": role, "content": content})

        # Optional: Add a system message at the top
        messages.insert(0, self.SYSTEMPROMPT)

        return messages