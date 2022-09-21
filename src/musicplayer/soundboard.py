import discord

from discord.ext import commands

from musicplayer.music import YTDLSource

uwu_count = 0


class Soundboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def soundboard(self, ctx):
        # We create the view and assign it to a variable so we can wait for it later.
        view = Sounds(self.bot, ctx)
        await ctx.send('What sound would you like to play?', view=view)
        # Wait for the View to stop listening for input...
        await view.wait()
        await ctx.channel.purge(limit=1)
        await self.soundboard(ctx)

    @soundboard.before_invoke
    async def ensure_voice(self, context):
        if context.voice_client is None:
            if context.author.voice:
                await context.author.voice.channel.connect()
            else:
                await context.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

class Sounds(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx

    async def play_sound(self, url, interaction: discord.Interaction):
        vc = self.ctx.voice_client
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='🏃')
    async def running(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=OIe2UbGKJQQ'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.grey,emoji='✨')
    async def uwu(self, interaction: discord.Interaction, button: discord.ui.Button):
        global uwu_count
        uwu_count += 1
        if uwu_count % 5 == 0:
            url = 'https://www.youtube.com/watch?v=WLsgxKQLRrY'
        else:
            url = 'https://www.youtube.com/watch?v=PqIMNE7QBSQ'

        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='🤡')
    async def chasing(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=aTyNKpoDwyM'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='❌')
    async def wrong(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=XW_-e-xQ_q8'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='🎯')
    async def headshot(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=ERzP8_tN9io'
        await self.play_sound(url, interaction)
