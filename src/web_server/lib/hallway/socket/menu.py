from typing import Dict

from flask import request
from flask_socketio import join_room

from src.web_server import session_user, sio, timing
from src.web_server.lib.hallway.hallway_hunters import HallwayHunters, Phases, games
from src.web_server.lib.hallway.commands import handle_developer_command
from src.web_server.lib.hallway.exceptions import InvalidAction, InvalidCommand
from src.web_server.lib.user_session import session_user_set


@sio.on("add_card", namespace="/hallway")
@timing
def get_state(data):
    room_id = int(data['room'])
    game = games[room_id]
    player = game.get_player(username=session_user())

    if player is None:
        return

    sio.emit("game_state", game.export_board(player), room=player.socket, namespace="/hallway")
