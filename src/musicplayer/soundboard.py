import discord

from discord.ext import commands

from src.musicplayer.music import YTDLSource

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

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='✨')
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

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='🐕')
    async def dog(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=SdmfidIYS84'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='😔')
    async def sad(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=7ODcC5z6Ca0'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='<a:sussy:938104411866152970>')
    async def sus(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=ekL881PJMjI'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='3️⃣')
    async def triple(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=XlLbsTP0C_U'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='5️⃣')
    async def pentakill(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=ewXkNOsx5dU'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='🦆')
    async def duck(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=aqCxlxclyzo'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='🍝')
    async def spaghet(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=0ynT_2DDBZg'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='💥')
    async def bonk(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=ZXK427oXjn8'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='🏳')
    async def failed(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=DQrUuRPDbwo'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='🪟')
    async def windows(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=Gb2jGy76v0Y'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='🔫')
    async def intervention(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=nL004eYKrEE'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='🏆')
    async def win(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.myinstants.com/media/sounds/all-i-do-is-win.mp3'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='👴')
    async def sheesh(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=YgT6XABqS5Y'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='🔥')
    async def supahot(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=Oys6-RrPPIE'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='☠')
    async def minecraftdead(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=eXdJYdCqdgE'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='🐵')
    async def monkey(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=NdlQqdJeV0Y'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='🇫')
    async def knew(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=gfXTcrxgNxY'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.red, emoji='🔄')
    async def flip(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=AHJEY6WCMmw'
        await self.play_sound(url, interaction)


    @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='📜')
    async def message(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=rIPq9Fl5r44'
        await self.play_sound(url, interaction)

    @discord.ui.button(label='', style=discord.ButtonStyle.green, emoji='<:imok:1005889577862574090>')
    async def whenyouhavetosayyouarefine(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=86f50Zqpgwo'
        await self.play_sound(url, interaction)

    # @discord.ui.button(label='', style=discord.ButtonStyle.blurple, emoji='<:imok:1005889577862574090>')
    # async def whenyousayyouarefine(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     url = 'https://www.youtube.com/watch?v=86f50Zqpgwo'
    #     await self.play_sound(url, interaction)





