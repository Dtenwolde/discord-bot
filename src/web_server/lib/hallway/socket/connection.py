from flask import request
from flask_socketio import join_room

from src.web_server import session_user, sio, timing
from src.web_server.lib.hallway.hallway_hunters import HallwayHunters, games
from src.web_server.lib.user_session import session_user_set


@sio.on('ping', namespace="/hallway")
def ping():
    sio.emit("pong", room=request.sid, namespace="/hallway")


@sio.on("set_session", namespace="/hallway")
@timing
def on_set_session(data):
    username = data.get("username", None)
    print(f"{username} connected.")
    if session_user() is None:
        session_user_set(username)

    sio.emit("set_session", username, room=request.sid, namespace="/hallway")


@sio.on("join", namespace="/hallway")
@timing
def on_join(data):
    room_id = int(data['room'])
    join_room(room=room_id)
    username = session_user()

    if room_id not in games:
        games[room_id] = HallwayHunters(room_id, username)

    game = games[room_id]
    game.add_player(username, request.sid)

    sio.emit("join", username, json=True, room=room_id, namespace="/hallway")
    game.update_players()


@sio.event(namespace="/hallway")
@timing
def disconnect():
    for room_id, game in games.items():
        print("Looking for disconnect...")
        player = game.get_player(socket_id=request.sid)
        if player:
            print("Found player!")
            game.remove_player(player.username)

            game.broadcast("%s left the game." % player.username)
            sio.emit("leave", player.username, json=True, room=room_id, namespace="/hallway")
