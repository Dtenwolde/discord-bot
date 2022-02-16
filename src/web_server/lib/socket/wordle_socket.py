from typing import Dict

import socketio
from flask import request
from flask_socketio import join_room

from database.repository import room_repository
from src.web_server import session_user, sio
from web_server.lib.wordle.WordleTable import WordlePhases, WordleTable, WordlePlayer

tables: Dict[int, WordleTable] = {}


@sio.on("ping", namespace="/wordle")
def on_ping():
    sio.emit("pong", room=request.sid, namespace="/wordle")


@sio.on("join", namespace="/wordle")
def on_join(data):
    room_id = int(data.get("room"))
    join_room(room_id)

    # Initialize table if this hasn't been done yet.
    room = room_repository.get_room(room_id)
    if room_id not in tables:
        tables[room_id] = WordleTable(room_id, author=room["author_id"])

    sio.emit("join", "message", json=True, room=room_id, namespace="/wordle")

    # Initialize player and add to table, then inform other players
    player = WordlePlayer(session_user(), request.sid, tables[room_id])
    tables[room_id].join(player)
    tables[room_id].broadcast_players()


@sio.on("start", namespace="/wordle")
def on_start(data):
    room_id = int(data.get("room"))

    profile = session_user()

    room = room_repository.get_room(room_id)

    table = tables[room_id]

    if room['author_id'] != profile['owner_id']:
        return

    table.initialize_round()
    sio.emit("start", None, room=room_id, namespace="/wordle")


@sio.on("word", namespace="/wordle")
def on_word(data):
    room_id = int(data.get("room"))
    guessed_word = data.get("word")

    table = tables[room_id]

    # Check if player is in this room
    profile = session_user()
    player = table.get_player(profile)
    if not player:
        print(f"{player} tried to send a word.")
        return

    response = table.check_word(player, guessed_word)
