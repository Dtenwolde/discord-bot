import asyncio
import configparser
import threading

import discord
from discord.ext import commands

from commands.chat import Chat
from commands.currency import Currency
from commands.reputation import Reputation
from database import create_all_models
from database.repository import music_repository, trigger_repository
from league_api import LeagueAPI
from musicplayer.musicplayer import MusicPlayer, Playlist
from src.musicplayer.youtube_search import YoutubeAPI
from src.settings import Settings


class Bot(commands.Bot):
    commands = {}

    def __init__(self, config, intents):
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)

        # Load config settings
        self.config = configparser.ConfigParser()
        self.settings = Settings()
        self.set_config(config)
        self.playlists = {}

        self.triggers = dict()

        self.music_player = MusicPlayer(self)
        self.youtube_api = YoutubeAPI(self.config["DEFAULT"]["YoutubeAPIKey"])
        self.league_api = LeagueAPI(self, self.config["DEFAULT"]["LeagueAPIKey"])

        self.asyncio_loop = asyncio.new_event_loop()
        self.asyncio_thread = threading.Thread(target=self.asyncio_loop.run_forever)

        self.asyncio_thread.start()
        self.league_api.payout_games.start()
        self.token = self.config["DEFAULT"]["DiscordAPIKey"]

        print("Done initializing.")

    def get_voice_by_guild(self, guild):
        for voice in self.voice_clients:
            if voice.guild == guild:
                return voice
        return None

    def update_triggers(self, message):
        self.triggers[message.guild] = trigger_repository.get_triggers(message.guild)

    def set_config(self, name):
        self.config.read(name)
        self.settings.page_size = int(self.config["DEFAULT"]["PageSize"])

    async def kill(self):
        # Waiting for handler thread to finish.
        self.asyncio_thread.join()

        music_repository.remove_unused()

        await self.logout()

    @classmethod
    def register_command(cls, *args):
        def wrapper(fn):
            for arg in args:
                if arg in cls.commands:
                    print("Warning: overwriting function with name %s." % arg)
                cls.commands[arg] = fn
            return fn

        return wrapper


intents = discord.Intents.default()
intents.members = True
bot = Bot("config.conf", intents=intents)

bot.add_cog(Reputation(bot))
bot.add_cog(bot.music_player)
bot.add_cog(Chat(bot))
bot.add_cog(Playlist(bot))
bot.add_cog(Currency(bot))
bot.add_cog(bot.league_api)

# Import models and create tables
import src.database.models.models  # noqa
create_all_models()

# Use event handlers for emotes etc.
import src.event_handlers.messages  # noqa