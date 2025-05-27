import re

# TODO... fill this out </3
FILTER = []

def filter_message(message: str) -> str:
    def replace_slur(match):
        word = match.group()
        return '*' * len(word)

    def replace_curse(match):
        word = match.group()
        return f'||{word}||'

    # Slurs replacement
    for slur in FILTER["slurs"]:
        pattern = re.compile(rf'\b{re.escape(slur)}\b', re.IGNORECASE)
        message = pattern.sub(replace_slur, message)

    # Curses wrapping
    for curse in FILTER["curses"]:
        pattern = re.compile(rf'\b{re.escape(curse)}\b', re.IGNORECASE)
        message = pattern.sub(replace_curse, message)

    return message