import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")

async def load_cogs():
    extensions = [
        "cogs.reminders",
        "cogs.polls",
        "cogs.ai",
        "cogs.music",
        "cogs.welcome"
    ]
    for ext in extensions:
        await bot.load_extension(ext)

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())