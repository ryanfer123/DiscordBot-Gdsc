import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def summarize(self, ctx, message_id: int = None):
        """Summarize a message: !summarize <message_id>"""
        try:
            if message_id:
                message = await ctx.channel.fetch_message(message_id)
            else:
                messages = [msg async for msg in ctx.channel.history(limit=2)]
                message = messages[1]

            prompt = f"Summarize the following text: {message.content}"
            response = gemini_model.generate_content(prompt)

            await ctx.send(f"**Summary:** {response.text}")

        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(AI(bot))