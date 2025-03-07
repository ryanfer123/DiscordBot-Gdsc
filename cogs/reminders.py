import datetime
from discord.ext import commands

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, time: str, *, message: str):
        """Set a reminder: !remind <time> <message>"""
        # Handle parsing and DB logic here
        await ctx.send(f"Reminder set for {time}: {message}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))
