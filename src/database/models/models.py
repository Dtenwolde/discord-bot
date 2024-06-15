from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Column, DateTime, ForeignKey, Float

from sqlalchemy.orm import relationship, mapped_column, Mapped

from database import db


class JSONAble():
    def __init__(self, **kwargs):
        for k, v in vars(kwargs):
            setattr(self, k, v)

    def to_json(self):
        def _is_valid(k, v):
            allowed_types = [str, int, bool, float, datetime]
            return (
                    not k.startswith("_") and
                    type(v) in allowed_types
            )

        return {k: v for k, v in self.__dict__.values() if _is_valid(k, v)}


class User(db.Model, JSONAble):
    __tablename__ = "user"

    discord_id = Column(Integer, primary_key=True)
    discord_username = Column(String)

    league_user_id = Column(Integer)
    balance = Column(Integer)
    active_playlist = Column(Integer)
    birthday = Column(DateTime)


class Trigger(db.Model, JSONAble):
    __tablename__ = "trigger"

    id = Column(Integer, primary_key=True)

    guild_id = Column(Integer)

    creator_id = mapped_column(ForeignKey("user.discord_id"))
    creator: Mapped["User"] = relationship("User")

    trigger = Column(String)
    response = Column(String)

    def __repr__(self):
        return "%s -> %s by %s (%s)" % (self.trigger, self.response, self.creator, self.guild_id)


class Report(db.Model, JSONAble):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)

    guild_id = Column(Integer)

    reportee_id: Mapped[int] = mapped_column(ForeignKey("user.discord_id"))
    reportee: Mapped["User"] = relationship(foreign_keys=[reportee_id])

    reporting_id = mapped_column(ForeignKey("user.discord_id"))
    reporting: Mapped["User"] = relationship(foreign_keys=[reporting_id])

    time = Column(DateTime, default=datetime.now())


class Honor(db.Model, JSONAble):
    __tablename__ = "honor"

    id = Column(Integer, primary_key=True)

    guild_id = Column(Integer)

    honoree_id = Column(ForeignKey("user.discord_id"))
    honoree = relationship("User", foreign_keys=[honoree_id])

    honoring_id = Column(ForeignKey("user.discord_id"))
    honoring = relationship("User", foreign_keys=[honoring_id])

    time = Column(DateTime, default=datetime.now())


class Song(db.Model, JSONAble):
    __tablename__ = "song"

    id = Column(Integer, primary_key=True)

    owner_id = Column(ForeignKey("user.discord_id"))
    owner = relationship("User")

    title = Column(String)
    url = Column(String)
    latest_playtime = Column(DateTime, default=datetime.now())


class Playlist(db.Model, JSONAble):
    __tablename__ = "playlist"

    id = Column(Integer, primary_key=True)

    owner_id = Column(ForeignKey("user.discord_id"))
    owner = relationship("User")
    title = Column(String)
    public = Column(Boolean, default=False)


class PlaylistSong(db.Model, JSONAble):
    __tablename__ = "playlist_song"

    id = Column(Integer, primary_key=True)

    playlist_id = Column(ForeignKey("playlist.id"))
    playlist = relationship("Playlist")

    song_id = Column(ForeignKey("song.id"))
    song = relationship("Song")


class LeagueGame(db.Model, JSONAble):
    __tablename__ = "league_game"

    id = Column(Integer, primary_key=True)

    owner_id = Column(ForeignKey("user.discord_id"))
    owner = relationship("User")

    amount = Column(Integer)
    type = Column(String)
    channel_id = Column(Integer)
    game_id = Column(Integer, default=None)
    team = Column(String, default=None)
    payed_out = Column(Boolean, default=False)


class EsportsGame(db.Model, JSONAble):
    __tablename__ = "esports_game"
    id = Column(Integer, primary_key=True)

    owner_id = Column(ForeignKey("user.discord_id"))
    owner = relationship("User")

    game_id = Column(Integer, default=None)

    amount = Column(Integer)
    odd = Column(Float)
    team = Column(String, default=None)
    channel_id = Column(Integer)

    processed = Column(Boolean, default=False)
    result = Column(String, default=None)


class GameRoom(db.Model, JSONAble):
    __tablename__ = "game_room"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    author_id = Column(ForeignKey("user.discord_id"))
    author = relationship("User")

    type = Column(String)
    created_datetime = Column(DateTime, default=datetime.now())

    message_id = Column(Integer)
