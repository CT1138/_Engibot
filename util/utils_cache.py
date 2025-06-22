import json
import os

STAR_SAVEPATH = "./__data/starboard_cache.json"

def starboard_save():
    with open(STAR_SAVEPATH, "w") as f:
        json.dump(starred_messages, f)

def starboard_load():
    global starred_messages
    if os.path.exists(STAR_SAVEPATH):
        with open(STAR_SAVEPATH, "r") as f:
            starred_messages = json.load(f)
    else:
        starred_messages = {}
