from datetime import datetime
from typing import List, Dict

from discord import Member

from src.database import database
from src.database.models.models import Song, Playlist, PlaylistSong


def add_music(song: Song):
    session = database.session()
    session.add(song)
    session.commit()


def get_music(owner: Member = None) -> List[Song]:
    session = database.session()

    if not owner:
        return session.query(Song).all()
    else:
        return session.query(Song).filter(Song.owner_id == owner.id).all()


def get_song(url: str) -> Song:
    session = database.session()
    return session.query(Song).filter(Song.url == url).one_or_none()


def get_song_by_id(_id):
    session = database.session()
    return session.query(Song).filter(Song.id == _id).one_or_none()


def remove_from_owner(url: str, owner_id: int):
    session = database.session()
    song = session.query(Song).filter(Song.owner_id == owner_id and Song.url == url).one_or_none()
    session.delete(song)
    session.commit()

    print(f"Removed {url} from {owner_id}")
    return song


def remove_unused():
    session = database.session()
    session.query(Song).filter(Song.owner_id == -1).delete()
    session.commit()


def remove_by_id(user: Member, lower, upper):
    session = database.session()

    songs_to_delete = get_music(user)[lower:upper]

    out = "```\n:x: Deleted:"
    for song in songs_to_delete:
        session.delete(song)
        out += f"- {song.title} ({song.url})\n"
    out += "```"
    session.commit()
    return out


def show_mymusic(mention, page=0, page_size=15):
    songs = get_music(mention)

    n_pages = int(len(songs) / page_size) + 1
    page = (page + n_pages) % n_pages

    out = "```\n%ss playlist (%d / %d):\n" % (mention.nick, (page + 1), n_pages)
    for i in range(page * page_size, min(len(songs), (page + 1) * page_size)):
        song = songs[i]
        out += "%d: %s | %s\n" % (i, song.title, song.owner.discord_username)
    out += "```"
    return out


def query_song_title(query):
    session = database.session()
    return session.query(Song).filter(Song.title.like(f"%{query}%")).all()


def get_playlist(owner, name):
    """
    Get the playlist with this name for this user, or create one if none exist.
    :param owner:
    :param name:
    :return:
    """
    if name is None:
        return None
    session = database.session()
    playlist = session.query(Playlist).filter(Playlist.owner_id == owner.id and Playlist.title == name).one_or_none()

    if not playlist:
        print("Creating new playlist:", name)
        playlist = Playlist(owner_id=owner.id, title=name, public=False)
        session.add(playlist)
        session.commit()

    return playlist


def get_playlist_songs(playlist: Playlist) -> List[Song]:
    session = database.session()

    return session.query(PlaylistSong).filter(PlaylistSong.playlist_id == playlist.id).all()
