from flask import request

from src.web_server import session_user, sio
from src.web_server.utils import timing
from src.web_server.lib.hallway.commands import handle_developer_command
from src.web_server.lib.hallway.exceptions import InvalidAction, InvalidCommand
from src.web_server.lib.hallway.hallway_hunters import games
from src.web_server.lib.hallway.Utils import Phases


@sio.on("game_state", namespace="/hallway")
@timing
def get_state(data):
    room_id = int(data['room'])

    game = games[room_id]

    username = session_user()
    player = game.get_player(username=username)
    if player is None:
        player = game.add_player(username, request.sid)

    sio.emit("game_state", game.export_board(player), room=player.socket, namespace="/hallway")


@sio.on("start", namespace="/hallway")
@timing
def start_game(data):
    room_id = int(data.get("room"))
    username = session_user()

    game = games[room_id]

    player = game.get_player(username=username)
    player.toggle_ready()

    # Only the owner may start the game
    if game.author != username:
        game.update_players()
        return

    sio.emit("loading", "Generating game...", room=room_id, namespace="/hallway")
    if not game.game_loop_thread.is_alive():
        game.game_loop_thread.start()

    game.start()

    sio.emit("start", None, room=room_id, namespace="/hallway")


@sio.on("changeColor", namespace="/hallway")
@timing
def change_color(data):
    room_id = int(data.get("room_id"))
    color = data.get("color")
    game = games[room_id]

    username = session_user()
    game.set_color(username, color)

    game.update_players()


@sio.on("action", namespace="/hallway")
@timing
def suggest_action(data):
    room_id = int(data.get("room"))
    action = data.get("action")
    game = games[room_id]
    if game.phase == Phases.NOT_YET_STARTED:
        return
    username = session_user()
    player = game.get_player(username)

    try:
        player.prepare_action(action, data.get("extra", None))
    except InvalidAction as e:
        sio.emit("message", e.message, room=player.socket, namespace="/hallway")


@sio.on("chat message", namespace="/hallway")
@timing
def message(data):
    room_id = int(data.get('room'))
    text_message = data.get('message')
    if text_message != "":  # Stop empty messages
        username = session_user()
        data["username"] = username
        if text_message[0] == "/":
            game = games[room_id]
            player = game.get_player(username)
            try:
                handle_developer_command(data, game)
            except InvalidCommand as e:
                sio.emit('command error', e.message, room=player.socket, include_self=True, namespace="/hallway")
        else:

            sio.emit('chat message', data, room=room_id, include_self=True, namespace="/hallway")
