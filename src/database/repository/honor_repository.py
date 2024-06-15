from datetime import datetime

from bson import SON
from sqlalchemy import func

from src.database.models.models import Honor
from src.database import database
import pymongo


def add_honor(honor: Honor):
    """
    Adds an Honor entry to the database.
    :param honor:
    :return:
    """

    session = database.session()
    session.add(honor)
    session.commit()


def get_honors():
    """
    Fetch all honors for this guild and order by count.
    :return:
    """

    session = database.session()
    return (session
            .query(Honor, func.count(Honor).label("total"))
            .group_by(Honor.honoree_id)
            .order_by("total DESC")
            .all())


def get_last_honor(guild, honoring):
    session = database.session()
    return (session
            .query(Honor)
            .filter(Honor.guild_id == guild.id and Honor.honoring_id == honoring.id)
            .order_by(Honor.c.id.desc())
            .one_or_none()
            )


def honor_allowed(guild, honoring):
    """
    Checks if this user can already honor for this guild.
    Returns None if the user can honor, or the time the user needs to wait.
    :param guild:
    :param honoring:
    :return:
    """
    honor = get_last_honor(guild, honoring)

    if honor is None:
        return None

    diff = datetime.now() - honor.time
    if diff.total_seconds() // 60 < 30:
        return 30 - diff.seconds // 60
    else:
        return None


def get_honor_count_by_id(user_id):
    session = database.session()
    return (session
            .query(Honor)
            .filter(Honor.honoree_id == user_id)
            .count()
            )
