import discord
from discord.ext.commands import Bot
from discord.ext import commands
from random import randint

client = discord.Client()
# bot_prefix = "!bot "
# client = commands.Bot(command_prefix=bot_prefix)

async def command_roll(message, args):
    if len(args) < 1:
        nmax = 100
    else:
        try:
            nmax = (int)(args[0])
        except:
            nmax = 100

    await client.send_message(message.channel, message.author.nick + " rolled a " + (str)(randint(0, nmax)))

@client.event
async def on_message(message):
    msg_array = message.content.split()
    cmd = msg_array[0]
    args = msg_array[1:]

    if cmd == '!ree':
        await client.send_message(message.channel, "<:REE:394490500960354304> <:REE:394490500960354304> \
                          <:REE:394490500960354304> <:REE:394490500960354304>")
    elif cmd == '!pubg':
        await client.send_message(message.channel, "<@&385799510879895552> time to die")

    elif cmd == "!roll":
        await command_roll(message, args)

# @client.command(pass_context=True)
# async def ree():
#     await client.say("<:REE:394490500960354304> <:REE:394490500960354304> \
#                       <:REE:394490500960354304> <:REE:394490500960354304>")
#
# @client.command(pass_context=True)
# async def pubg():
#     await client.say("<@&385799510879895552> time to die")


client.run("MzQwMTk3NjgxMzExNzc2NzY4.DSQ39A.sGYDQgt8-5lbOK7N0L5EDQRAatk")
