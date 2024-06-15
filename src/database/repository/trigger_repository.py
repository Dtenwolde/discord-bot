from typing import Optional, List

from discord import Guild

from src.database import db
from src.database.models.models import Trigger


def get_triggers(guild: Guild) -> List[Trigger]:
    if guild is None:
        return None

    session = db.session
    return session.query(Trigger).filter(Trigger.guild_id == guild.id).all()


def get_trigger(guild: Guild, name: str) -> Optional[Trigger]:
    session = db.session
    return session.query(Trigger).filter(Trigger.guild_id == guild.id and Trigger.trigger == name).one_or_none()


def remove_trigger(guild: Guild, name: str):
    trigger = get_trigger(guild, name)
    session = db.session
    session.delete(trigger)
    session.commit()


def add_trigger(trigger: Trigger):
    if len(trigger.trigger) < 3 or len(trigger.trigger) > 50:
        return "Trigger length has to be 3 < n < 50"

    session = db.session
    existing = session.query(Trigger).filter(
        Trigger.guild_id == trigger.guild_id and Trigger.trigger == trigger.trigger).one_or_none()

    if existing:
        raise RuntimeError("This trigger already exists.")

    session.add(trigger)
    session.commit()