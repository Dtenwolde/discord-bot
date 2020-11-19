from database.repository import music_repository
from src import bot
from src.custom_emoji import CustomEmoji


async def generate_help(channel):
    docs = "```"
    for key in bot.commands.keys():
        fun = bot.commands[key]
        # Catch if there is no documentation known for this function.
        try:
            docs += fun.__doc__.strip().split("\n", 1)[0] + "\n"
        except AttributeError as e:
            docs += "!%s: ???\n" % key

    await channel.send(docs + "```")


@bot.event
async def on_message(message):
    if message.guild not in bot.triggers:
        bot.update_triggers(message)

    await bot.process_commands(message)

    # Command handling
    if message.content.startswith(bot.PREFIX):
        msg_array = message.content.split(" ")

        if len(msg_array) == 0:
            return

        cmd = msg_array[0][1:]
        args = msg_array[1:]
        if cmd == "help":
            await generate_help(message.channel)
        elif cmd in bot.commands:
            await bot.commands[cmd](args, message)
    # Default message handler
    else:
        if message.author.bot:
            return

        for trigger in bot.triggers[message.guild]:
            if trigger.trigger in message.content:
                await message.channel.send(trigger.response)


@bot.event
async def on_reaction_add(reaction, user):
    # Dont delete if bot adds reaction
    if user == bot.client.user:
        return

    # Dont delete if its not a message from bot.
    if reaction.message.author != bot.client.user:
        return

    if str(reaction.emoji)[1:-1] == CustomEmoji.jimbo:
        await reaction.message.delete()

    lc = str(reaction.emoji) == CustomEmoji.arrow_left
    rc = str(reaction.emoji) == CustomEmoji.arrow_right
    if lc or rc:
        mention, page = music_repository.playlists[reaction.message.id]
        page = page - 1 if lc else page + 1
        out = music_repository.show_playlist(mention, page)
        music_repository.playlists[reaction.message.id] = (mention, page)
        await reaction.message.edit(content=out)


