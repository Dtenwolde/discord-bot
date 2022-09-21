import discord

from discord.ext import commands

from musicplayer.music import YTDLSource


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

    @soundboard.before_invoke
    async def ensure_voice(self, context):
        if context.voice_client is None:
            if context.author.voice:
                await context.author.voice.channel.connect()
            else:
                await context.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


class Buttons(discord.ui.View):
    def __init__(self, bot, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label="Blurple Button", style=discord.ButtonStyle.blurple)  # or .primary
    async def blurple_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Got blurple")
        button.disabled = True
        url = 'https://www.youtube.com/watch?v=OIe2UbGKJQQ'
        vc = self.ctx.voice_client
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await interaction.response.defer()


    @discord.ui.button(label="Gray Button", style=discord.ButtonStyle.gray)  # or .secondary/.grey
    async def gray_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Got gray")
        button.disabled = True
        await interaction.response.defer()


    @discord.ui.button(label="Green Button", style=discord.ButtonStyle.green)  # or .success
    async def green_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Got green")
        button.disabled = True
        await interaction.response.defer()


    @discord.ui.button(label="Red Button", style=discord.ButtonStyle.red)  # or .danger
    async def red_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Got red")
        button.disabled = True
        await interaction.response.defer()


    # @discord.ui.button(label="Change All", style=discord.ButtonStyle.success)
    # async def color_changing_button(self, child: discord.ui.Button, interaction: discord.Interaction):
    #     for child in self.children:
    #         child.disabled = True
    #     await interaction.response.edit_message(view=self)


class Sounds(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Running', style=discord.ButtonStyle.green)
    async def running(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = 'https://www.youtube.com/watch?v=OIe2UbGKJQQ'
        vc = self.ctx.voice_client
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
        # await interaction.response.send_message('Cancelling', ephemeral=True)
        # self.value = False
        # self.stop()

