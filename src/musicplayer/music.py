import asyncio
import queue

import discord
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


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
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn -dn -ignore_unknown -sn',
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
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = queue.Queue()

    @commands.command()
    async def join(self, context):
        """Joins a voice channel"""
        """
        !join: lets the bot join the voice channel of the person who requested.
        """
        if context.author.voice is not None:
            try:
                await context.author.voice.channel.connect()
            except discord.ClientException:
                await context.channel.send("I have already joined a voice channel.")
        else:
            await context.channel.send("You are not in a voice channel.")

    @commands.command()
    async def play(self, context):
        if self.queue.empty():
            await context.channel.send("No songs in the queue")
            return
        vc = context.voice_client
        url = self.queue.get()
        async with context.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{player.title}"))



    @commands.command()
    async def queue(self, context, *, url):
        self.queue.put(url)
        await context.send(f"Queued {url}")

    # @commands.command()
    # async def play(self, context, *, query):
    #     """Plays a file from the local filesystem"""
    #
    #     source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
    #     context.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
    #
    #     await context.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, context, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with context.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            context.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await context.send(f'Now playing: {player.title}')

    @commands.command()
    async def fuckoff(self, context):
        """
        Makes the bot leave its currently active voice channel.
        """
        await context.voice_client.disconnect()

    @commands.command()
    async def stream(self, context, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        vc = context.voice_client
        if vc.is_playing():
            self.queue.put(url)
            await context.send(f"Already playing a song, put {url} in queue")
            return
        async with context.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await context.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, context, volume: int):
        """Changes the player's volume"""

        if context.voice_client is None:
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await context.send(embed=embed)

        context.voice_client.source.volume = volume / 100
        await context.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, context):
        """Stops and disconnects the bot from voice"""

        await context.voice_client.disconnect()

    @commands.command()
    async def pause(self, context):
        """Pause the currently playing song."""
        vc = context.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await context.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await context.send("Paused ⏸️")

    @commands.command(name='resume', description="resumes music")
    async def resume_(self, context):
        """Resume the currently paused song."""
        vc = context.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await context.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await context.send("Resuming ⏯️")

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, context):
        if context.voice_client is None:
            if context.author.voice:
                await context.author.voice.channel.connect()
            else:
                await context.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")