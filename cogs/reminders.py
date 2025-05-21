import asyncio
import datetime
from discord.ext import commands

def parse_time_str(time_str: str) -> int:
    """Converts a time string like "10m", "1h", "30s" into seconds."""
    multipliers = {'s': 1, 'm': 60, 'h': 3600}
    unit = time_str[-1].lower()
    if unit not in multipliers:
        raise ValueError("Invalid time unit. Use 's', 'm', or 'h'.")
    try:
        value = int(time_str[:-1])
        if value <= 0:
            raise ValueError("Time value must be positive.")
        return value * multipliers[unit]
    except ValueError:
        raise ValueError("Invalid time format. Must be like '10s', '5m', '1h'.")

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, time_str: str, *, message: str):
        """Set a reminder: !remind <time_str> <message> (e.g., !remind 10m Check email)"""
        try:
            total_seconds = parse_time_str(time_str)
        except ValueError as e:
            await ctx.send(f"❌ Error: {e}")
            return

        await ctx.send(f"👍 Okay, I will remind you in {time_str} about: {message}")

        async def reminder_task():
            await asyncio.sleep(total_seconds)
            await ctx.send(f"{ctx.author.mention}, here's your reminder: {message}")

        asyncio.create_task(reminder_task())

async def setup(bot):
    await bot.add_cog(Reminders(bot))
