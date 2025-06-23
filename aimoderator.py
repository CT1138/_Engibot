from openai import OpenAI
from interface.interface_json import IF_JSON
import json
import os

TOKENS = IF_JSON("./__data/tokens.json").json
client = OpenAI(api_key=TOKENS["openai"])

modModel = "omni-moderation-latest"
sensitive_categories = ["hate", "harassment", "sexual", "self-harm"]

class AIModerator:
    def __init__(self):
        self.categories_to_flag = sensitive_categories
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

def scan_all_responses(moderator):
    input_path = os.path.join(".", "__data", "responses.json")
    output_path = "responses_filtered.txt"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    responses = data.get("random", {}).get("_responses", [])
    urls = data.get("random", {}).get("_urls", [])

    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write("Source\tFlagged\tFlaggedCategories\tContent\n")

        # Scan _responses
        for i, text in enumerate(responses):
            print("Scanning: " + text)
            flagged, response = moderator.scanText(text)
            result = response.results[0]
            categories = dict(result.categories)
            triggered = [cat for cat, val in categories.items() if val]
            out_file.write(f"_responses\t{flagged}\t{','.join(triggered)}\t{text}\n")

        # Scan _urls
        for i, url in enumerate(urls):
            print("Scanning: " + url)
            flagged, response = moderator.scanText(url)
            result = response.results[0]
            categories = dict(result.categories)
            triggered = [cat for cat, val in categories.items() if val]
            out_file.write(f"_urls\t{flagged}\t{','.join(triggered)}\t{url}\n")

    print(f"Scan results written to {output_path}")