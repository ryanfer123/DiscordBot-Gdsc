import os
import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import asyncio
import aiohttp
import google.generativeai as genai
import youtube_dl
import wavelink

# Environment Variables and Configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN=MTM0Njg0MjE1NzEwNTAyMTA3MQ.GFjeXj.r85BQZNI-Z6oGezc8Coyze0Sfm_KIslsTB5jEw')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY=AIzaSyDkCZlqvcq-Q4O_lo96hcwf3y68qdAZYbQ')

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix='!', intents=intents)

        # Database initialization
        self.conn = sqlite3.connect('bot_database.db')
        self.create_tables()

        # Reminder tracking
        self.reminder_check.start()

    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()

        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                channel_id INTEGER,
                reminder_text TEXT,
                reminder_time DATETIME
            )
        ''')

        # Polls table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                message_id INTEGER,
                question TEXT,
                options TEXT,
                creator_id INTEGER
            )
        ''')

        self.conn.commit()

    async def setup_hook(self):
        """Setup wavelink for music functionality"""
        node = await wavelink.NodePool.create_node(
            bot=self,
            host='localhost',
            port=2333,
            password='youshallnotpass'
        )

    @tasks.loop(minutes=1)
    async def reminder_check(self):
        """Check and send due reminders"""
        cursor = self.conn.cursor()
        now = datetime.datetime.now()

        cursor.execute('''
            SELECT id, user_id, channel_id, reminder_text 
            FROM reminders 
            WHERE reminder_time <= ?
        ''', (now,))

        due_reminders = cursor.fetchall()

        for reminder in due_reminders:
            reminder_id, user_id, channel_id, reminder_text = reminder
            channel = self.get_channel(channel_id)
            user = await self.fetch_user(user_id)

            if channel:
                await channel.send(f"{user.mention} Reminder: {reminder_text}")

            # Delete the reminder after sending
            cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))

        self.conn.commit()

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

    async def on_member_join(self, member):
        """Custom welcome message"""
        welcome_channel = member.guild.system_channel
        if welcome_channel:
            await welcome_channel.send(
                f"Welcome to the server, {member.mention}! 🎉 "
                f"We're excited to have you join our community. "
                f"Feel free to introduce yourself and have fun!"
            )

class RemindersExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remind')
    async def set_reminder(self, ctx, *, reminder_info):
        """Set a reminder with format: !remind <time> <message>"""
        try:
            # Parse time and message (you'd want a more robust parsing method)
            time_str, *message = reminder_info.split(' ', 1)
            reminder_time = datetime.datetime.fromisoformat(time_str)
            reminder_text = ' '.join(message)

            cursor = self.bot.conn.cursor()
            cursor.execute('''
                INSERT INTO reminders 
                (user_id, channel_id, reminder_text, reminder_time) 
                VALUES (?, ?, ?, ?)
            ''', (ctx.author.id, ctx.channel.id, reminder_text, reminder_time))

            self.bot.conn.commit()
            await ctx.send(f"Reminder set for {reminder_time}")

        except Exception as e:
            await ctx.send(f"Error setting reminder: {str(e)}")

class PollExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='poll')
    async def create_poll(self, ctx, question, *options):
        """Create a poll with a question and options"""
        if len(options) < 2:
            await ctx.send("Please provide at least two options for the poll.")
            return

        # Construct poll message
        poll_message = f"**{question}**\n\n"
        for i, option in enumerate(options, 1):
            poll_message += f"{i}. {option}\n"

        poll_msg = await ctx.send(poll_message)

        # Add reaction options
        for i in range(1, len(options) + 1):
            await poll_msg.add_reaction(f'{i}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}')

        # Store poll in database
        cursor = self.bot.conn.cursor()
        cursor.execute('''
            INSERT INTO polls 
            (channel_id, message_id, question, options, creator_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (ctx.channel.id, poll_msg.id, question, ','.join(options), ctx.author.id))

        self.bot.conn.commit()

class AIExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='summarize')
    async def summarize_message(self, ctx, message_id: int = None):
        """Summarize a message using Gemini AI"""
        try:
            if message_id:
                message = await ctx.channel.fetch_message(message_id)
            else:
                # Get previous message if no ID specified
                messages = await ctx.channel.history(limit=2).flatten()
                message = messages[1]  # First message is the command itself

            # Use Gemini to generate summary
            prompt = f"Summarize the following text concisely: {message.content}"
            response = gemini_model.generate_content(prompt)

            await ctx.send(f"**Summary:**\n{response.text}")

        except Exception as e:
            await ctx.send(f"Error generating summary: {str(e)}")

class MusicExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}  # Per-server music queue

    @commands.command(name='play')
    async def play_music(self, ctx, *, query: str):
        """Play a song or add to queue"""
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        player = ctx.voice_client

        # Search for track
        tracks = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            return await ctx.send('No tracks found.')

        track = tracks[0]

        # Add to queue or play immediately
        if player.is_playing():
            if ctx.guild.id not in self.queue:
                self.queue[ctx.guild.id] = []
            self.queue[ctx.guild.id].append(track)
            await ctx.send(f'Added to queue: {track.title}')
        else:
            await player.play(track)
            await ctx.send(f'Now playing: {track.title}')

    @commands.command(name='queue')
    async def show_queue(self, ctx):
        """Show current music queue"""
        if ctx.guild.id not in self.queue or not self.queue[ctx.guild.id]:
            return await ctx.send('Queue is empty.')

        queue_list = self.queue[ctx.guild.id]
        queue_message = "Current Queue:\n" + "\n".join(
            f"{i+1}. {track.title}" for i, track in enumerate(queue_list)
        )
        await ctx.send(queue_message)

def main():
    bot = DiscordBot()

    # Add extensions
    bot.add_cog(RemindersExtension(bot))
    bot.add_cog(PollExtension(bot))
    bot.add_cog(AIExtension(bot))
    bot.add_cog(MusicExtension(bot))

    bot.run(TOKEN)

if __name__ == '__main__':
    main()