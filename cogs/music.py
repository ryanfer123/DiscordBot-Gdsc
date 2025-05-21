import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    @commands.command(name='join', help='Joins a voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send('You are not connected to a voice channel.')
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f'Connected to {channel.name}')

    @commands.command(name='leave', help='Leaves the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Disconnected from voice channel.')
        else:
            await ctx.send('Not connected to a voice channel.')

    @commands.command(name='play', help='Plays music from a YouTube URL')
    async def play(self, ctx, *, url):
        if not ctx.voice_client:
            await self.join(ctx)
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                ctx.voice_client.play(
                    player, after=lambda e: print(f'Player error: {e}') if e else None
                )
                server_id = ctx.guild.id
                if server_id not in self.queues:
                    self.queues[server_id] = []
                self.queues[server_id].append(player)
                await ctx.send(f'Now playing: {player.title}')
            except Exception as e:
                await ctx.send(f'An error occurred: {e}')

    @commands.command(name='queue', help='Shows the current music queue')
    async def queue(self, ctx):
        server_id = ctx.guild.id
        if server_id not in self.queues or not self.queues[server_id]:
            await ctx.send('Queue is empty.')
            return
        queue_list = '\n'.join([f'{i+1}. {song.title}' for i, song in enumerate(self.queues[server_id])])
        await ctx.send(f'Current queue:\n{queue_list}')

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('Playback paused.')
        else:
            await ctx.send('Nothing is playing right now.')

    @commands.command(name='resume', help='Resumes the paused song')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('Playback resumed.')
        else:
            await ctx.send('Nothing is paused right now.')

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Skipped the current song.')
        else:
            await ctx.send('Nothing is playing right now.')

    @commands.command(name='volume', help='Changes the player volume')
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')
        if 0 <= volume <= 100:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f'Volume set to {volume}%')
        else:
            await ctx.send('Volume must be between 0 and 100')


# Setup function
async def setup(bot):
    await bot.add_cog(Music(bot))
