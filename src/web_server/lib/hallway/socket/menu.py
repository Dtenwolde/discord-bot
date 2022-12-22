from src.web_server import session_user, sio, timing
from src.web_server.lib.hallway.hallway_hunters import games


@sio.on("add_card", namespace="/hallway")
@timing
def get_state(data):
    room_id = int(data['room'])
    game = games[room_id]
    player = game.get_player(username=session_user())

    if player is None:
        return

    player.deck.add_card_to_deck(data.get("card_name"))
    player.deck.emit_deck()


@sio.on("remove_card", namespace="/hallway")
@timing
def get_state(data):
    room_id = int(data['room'])
    game = games[room_id]
    player = game.get_player(username=session_user())

    if player is None:
        return

    player.deck.remove_card_from_deck(data.get("card_name"))
    player.deck.emit_deck()
