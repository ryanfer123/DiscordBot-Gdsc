import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Play music: !play <song name or URL>"""
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a voice channel.")

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        player = ctx.voice_client

        tracks = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            return await ctx.send("❌ No tracks found.")

        track = tracks[0]

        if player.is_playing():
            self.queue.setdefault(ctx.guild.id, []).append(track)
            await ctx.send(f"➕ Added to queue: {track.title}")
        else:
            await player.play(track)
            await ctx.send(f"🎶 Now playing: {track.title}")

    @commands.command()
    async def queue(self, ctx):
        """Show the current music queue: !queue"""
        guild_queue = self.queue.get(ctx.guild.id, [])
        if not guild_queue:
            await ctx.send("📭 The queue is empty.")
        else:
            queue_list = "\n".join(f"{i+1}. {track.title}" for i, track in enumerate(guild_queue))
            await ctx.send(f"**Queue:**\n{queue_list}")

async def setup(bot):
    await bot.add_cog(Music(bot))