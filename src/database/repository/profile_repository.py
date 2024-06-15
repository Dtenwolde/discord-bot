import logging
from functools import wraps
from time import time

from discord import User

from database import db
from src.database.models import models


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger = logging.getLogger("timing")
        logger.info(f"{f.__name__}: {te - ts}")
        return result

    return wrap


def get_profile(user: User = None, user_id: int = None, username: str = None):
    session = db.session

    db_user = None
    # Get the usermodel from either method
    if user is not None:
        db_user = session.query(models.User).filter(models.User.discord_id == user.id).one_or_none()
    elif user_id is not None:
        db_user = session.query(models.User).filter(models.User.discord_id == user_id).one_or_none()
    elif username is not None:
        db_user = session.query(models.User).filter(models.User.name == user.name).one_or_none()

    if not db_user:
        db_user = models.User(discord_username=user.name, discord_id=user.id, balance=500)
        session.add(db_user)
        session.commit()

    return db_user


def add_birthday(user: models.User, birthday):
    session = db.session
    user.birthday = birthday
    session.commit()
    return user


def update_money(user: models.User, money_update):
    session = db.session
    user.balance = max(user.balance + money_update, 0)
    session.commit()
    return user


def update_active_playlist(profile: models.User, value):
    session = db.session
    profile.active_playlist = value
    session.commit()
    return profile
