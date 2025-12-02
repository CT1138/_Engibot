import random
import discord
import asyncio
from discord.ext import commands as dCommands
from interface.interface_response import IF_Response, ResultType

class hGames(dCommands.Cog):
    def __init__(self, bot):
        self.RESPONSE = IF_Response()
        self.bot = bot

    @dCommands.hybrid_group(name="games", with_app_command=True, invoke_without_command=True)
    async def games(self, ctx):
        await ctx.defer()
        RESPONSE = await self.RESPONSE.getRandom("failedKill", result_type=ResultType.RESPONSE)
        await ctx.send(RESPONSE)

    @games.command(name="guess", with_app_command=True, invoke_without_command=True)
    @discord.app_commands.describe(guess="Your guess (a number between 1 and 10)", min="Minimum value, defaults to 0", max="Maximum value, defaults to 10")
    async def guess(self, ctx: dCommands.Context, guess: int, min: int = 0, max: int = 10):
        await ctx.defer()
        URL = await self.RESPONSE.getRandom("random", result_type=ResultType.URL)

        if min > max:
            await ctx.send("⚠️ You provided a larger minimum value than maximum!")
            return

        if guess < min or guess > max:
            await ctx.send(f"Please guess a number **between {min} and {max}**.")
            return

        bot_number = random.randint(min, max)

        if guess == bot_number:
            await ctx.send(f"🎉 Correct! You guessed **{guess}** and I picked **{bot_number}**.")
            return

        if guess < bot_number:
            hint_upper = random.randint(bot_number + 1, max) if bot_number < max else max
            hint = f"greater than **{guess}** and less than **{hint_upper}**"
        else:
            hint_lower = random.randint(min, bot_number - 1) if bot_number > min else min
            hint = f"less than **{guess}** and greater than **{hint_lower}**"

        await ctx.send(
            f"❌ Not quite! You guessed **{guess}**, but the correct number is {hint}. Try again!"
            f"\nPlease enter your new guess (between {min} and {max}):"
        )

        def check(m: discord.Message):
            return (
                m.author == ctx.author and
                m.channel == ctx.channel and
                m.content.isdigit()
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
            second_guess = int(msg.content)

            if second_guess == bot_number:
                await ctx.send(f"🎯 Nice! You got it on the second try — the number was **{bot_number}**.")
                await ctx.send(URL)
            else:
                await ctx.send(f"🙈 Nope, the number was **{bot_number}**. Better luck next time!")
                await ctx.send(URL)
        except asyncio.TimeoutError:
            await ctx.send(f"⌛ You took too long to respond! The number was **{bot_number}**.")


    @games.command(name="rock-paper-scissors", with_app_command=True, invoke_without_command=True)
    @discord.app_commands.describe(move="Your move (Rock, Paper, or Scissors)")
    async def rps(self, ctx: dCommands.Context, move=""):
        await ctx.defer()

        choices = {
            "r": "Rock",
            "p": "Paper",
            "s": "Scissors"
        }

        user_input = move.lower()[0]
        user_choice = choices.get(user_input)

        if not user_choice:
            await ctx.send("Invalid move. Please choose Rock, Paper, or Scissors.")
            return

        bot_choice = random.choice(list(choices.values()))

        # Determine result
        if user_choice == bot_choice:
            result = f"It's a tie! We both chose **{user_choice}**."
        elif (
            (user_choice == "Rock" and bot_choice == "Scissors") or
            (user_choice == "Paper" and bot_choice == "Rock") or
            (user_choice == "Scissors" and bot_choice == "Paper")
        ):
            result = f"You win! You chose **{user_choice}** and I chose **{bot_choice}**."
        else:
            result = f"You lose! You chose **{user_choice}** and I chose **{bot_choice}**."

        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(hGames(bot))
