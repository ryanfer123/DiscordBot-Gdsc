import discord
from discord.ext import commands
import aiosqlite

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, question: str, *options):
        """Create a poll: !poll <question> <option1> <option2> ..."""
        if len(options) < 2:
            await ctx.send("❌ Please provide at least two options.")
            return
        if len(options) > 10:
            await ctx.send("❌ Maximum of 10 options allowed.")
            return

        description = "\n".join(f"{i+1}. {option}" for i, option in enumerate(options))
        embed = discord.Embed(title=question, description=description, color=discord.Color.blue())
        poll_message = await ctx.send(embed=embed)

        emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        for i in range(len(options)):
            await poll_message.add_reaction(emoji_numbers[i])

        async with aiosqlite.connect('bot_database.db') as db:
            await db.execute(
                "INSERT INTO polls (channel_id, message_id, question, options, creator_id) VALUES (?, ?, ?, ?, ?)",
                (ctx.channel.id, poll_message.id, question, ','.join(options), ctx.author.id)
            )
            await db.commit()

async def setup(bot):
    await bot.add_cog(Polls(bot))