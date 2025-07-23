from openai import OpenAI
from google.cloud import vision
import requests
import io, os
from interface.interface_json import IF_JSON
from interface.interface_guild import IF_Guild
import discord

TOKENS = IF_JSON("./__data/tokens.json").json
client = OpenAI(api_key=TOKENS["openai"])

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/tyler/_Engibot/__data/google-api.key.json"
modModel = "omni-moderation-latest"
with open("./__data/aiPrompt.txt", "r", encoding="utf-8") as file:
    basePrompt = file.read()


class IF_GPT:
    def __init__(self, model="gpt-4o", temperature=0.2, systemPrompt=""):
        self.model=model
        self.temperature=temperature
        self.systemPrompt=systemPrompt + "\n" + basePrompt

    def chat(self, input, additionalprompt=""):
        input.insert(0, {"role": "system", "content": additionalprompt})
        input.insert(0, {"role": "system", "content": basePrompt})
        print(f"input: {input}")
        response = client.responses.create(
            model=self.model,
            input=input,
            temperature=self.temperature
            )
        print(f"output: {response.output_text}")
        return response.output_text
    
    def download_image(self, url, save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        else:
            raise Exception("Failed to download image.")
    
    def analyze_image(self, image_url):
        path = "/tmp/readimg.png"
        try:
            client = vision.ImageAnnotatorClient()
            self.download_image(image_url, path)
            with io.open(path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = client.label_detection(image=image)
            labels = response.label_annotations

            descriptions = [label.description for label in labels]
            return ', '.join(descriptions)

            print("Labels:")
            print(labels)
            for label in labels:
                print(label.description)
            return labels
        finally:
            if os.path.exists(path):
                os.remove(path)
        

class IF_MODERATOR:
    def __init__(self, guild: discord.Guild):
        self.GUILD = IF_Guild(guild)
        self.categories_to_flag = []
        return
    
    async def initialize(self):
        # Load the categories to flag from the guild configuration
        await self.GUILD.initialize()
        if self.GUILD.Config["sensitive_content"]:
            self.categories_to_flag = self.GUILD.Config["sensitive_content"]
        else:
            # Default categories if none are set
            self.categories_to_flag = ["hate", "harassment", "sexual", "self-harm"]
    
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