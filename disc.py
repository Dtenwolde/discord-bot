import asyncio
import functools
import os
import pathlib

import typing

from src import bot_run, add_all_cogs


def create_directories():
    pathlib.Path("storage").mkdir(parents=True, exist_ok=True)
    pathlib.Path("storage/data").mkdir(parents=True, exist_ok=True)
    pathlib.Path("storage/models").mkdir(parents=True, exist_ok=True)
    print("Created directories")


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapper = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapper)
    return wrapper


@to_thread
def main():
    create_directories()
    from src import bot

    bot.initialize()
    add_all_cogs(bot)
    asyncio.run(bot_run())
    # bot.run(bot.token)





if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
