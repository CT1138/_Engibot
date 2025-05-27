import discord
from util import utils_json
PATH = "./__data/commands.json"
JSON = utils_json.read(PATH)

def help():
    embed = discord.Embed(title="Command Help", color=discord.Color.blue())
    for command_name, command_info in JSON.items():
        description = command_info.get("_desc", "No description provided.")
        params = []
        for key, value in command_info.items():
            if key.startswith("_param"):
                param_name = value.get("_name", "Unnamed")
                param_desc = value.get("_desc", "No description.")
                optional = value.get("_optional", 0)
                param_str = f"  • **{param_name}**: {param_desc}"
                if optional:
                    param_str += " **(Optional)**"
                params.append(param_str)
        field_value = description
        if params:
            field_value += "\n\n" + "\n".join(params)
        embed.add_field(name=command_name, value=field_value, inline=False)
    return embed
