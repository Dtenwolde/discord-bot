import asyncio
import configparser
import json
import re
from collections import defaultdict

import discord
from tqdm import tqdm
from discord.ext.commands import Bot

config = configparser.ConfigParser()
config.read("config.conf")
token = config["DEFAULT"]["DiscordAPIKey"]

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    stonk = bot.get_guild(188638113982185472)
    print(stonk.channels)

    general_id = 188638113982185472

    channel = stonk.get_channel(general_id)

    # emote_counter = defaultdict(int)
    # re.match(r"<:[a-zA-Z]+:\d+>", message.content)

    result = []
    bar = tqdm()
    n = 0
    async for message in channel.history(limit=None):
        result.append({
            "sender": message.author.name,
            "message": message.content,
        })
        bar.update(1)
        n += 1
        if n % 1e4 == 1e4-1:
            with open(f"stonkzgeneral_{int(n // 1e4)}.json", "w+") as f:
                d = json.dump(f, result)
                f.write(d)

            print(len(result))


async def main():
    async with bot:
        await bot.start(token)

def reg():
    # emote_counter = defaultdict(int)
    # re.match(r"<:[a-zA-Z]+:\d+>", message.content)

    result = []
    bar = tqdm()
    n = 0
    async for message in channel.history(limit=None):
        result.append({
            "sender": message.author.name,
            "message": message.content,
        })
        bar.update(1)
        n += 1
        if n % 1e4 == 1e4 - 1:
            with open(f"stonk_general_{int(n // 1e4)}.json", "w+") as f:
                d = json.dumps(result)
                f.write(d)

            print(len(result))


if __name__ == "__main__":
    # asyncio.run(main())
    reg()