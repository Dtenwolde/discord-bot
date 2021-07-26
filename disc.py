import os
import pathlib


def create_directories():
    pathlib.Path("storage").mkdir(parents=True, exist_ok=True)
    pathlib.Path("storage/data").mkdir(parents=True, exist_ok=True)
    pathlib.Path("storage/models").mkdir(parents=True, exist_ok=True)


def main():
    create_directories()

    from src import bot

    # Import and setup database models
    from src.database import Base, db
    Base.metadata.create_all(db.engine)

    bot.run(bot.token)


if __name__ == "__main__":
    main()
