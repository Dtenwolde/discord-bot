from src.web_server import sio
from src.web_server.lib.hallway.cards.card import available_cards
from src.web_server.lib.hallway.entities.player_class import PlayerClass
from src.web_server.lib.hallway.exceptions import InvalidAction
from src.web_server.lib.hallway.storage.database import db
from src.web_server.lib.hallway.storage.model import StoredDeck


class Deck:
    """
    A deck is a player-bound class which contains all the cards currently in play.
    It also has a list of all available cards for this specific player.
    The list of available cards for a player will be stored in a database and be consistent across multiple instances.
    """
    MAX_DECK_SIZE = 20

    def __init__(self, player: PlayerClass):
        self.player = player

        # Active deck and remaining cards are lists of card_names.
        self.active_deck = []
        self.remaining_cards = []

        self.update_cards_for_player()

    def add_card_to_deck(self, card_name):
        if card_name not in available_cards.keys():
            raise InvalidAction("You tried to add a card which doesn't exist.")

        if len(self.active_deck) == self.MAX_DECK_SIZE:
            raise InvalidAction(
                f"Your deck already contains the maximum allowed amount ({self.MAX_DECK_SIZE}) of cards.")

        if card_name not in self.remaining_cards:
            raise InvalidAction(f"You do not have any '{card_name}' left.")

        # Remove from remaining cards and add to deck
        self.remaining_cards.remove(card_name)
        self.active_deck.append(card_name)

    def remove_card_from_deck(self, card_name):
        if card_name not in self.active_deck:
            raise InvalidAction("You tried to remove a card which was not in your deck.")

        self.active_deck.remove(card_name)
        self.remaining_cards.append(card_name)

    def emit_deck(self):
        sio.emit("deck_cards", [available_cards[card_name].to_json() for card_name in self.active_deck],
                 room=self.player.socket, namespace="/hallway")

    def emit_remaining(self):
        sio.emit("remaining_cards", [available_cards[card_name].to_json() for card_name in self.remaining_cards],
                 room=self.player.socket, namespace="/hallway")

    def update_cards_for_player(self):
        """
        Gets the currently active deck for a player, and sets the remaining cards based on current deck.
        :return:
        """
        # Fetch data object and remove it from the database session to get a freely editable object
        session = db.session()
        deck = session.query(StoredDeck).filter(StoredDeck.player_name == self.player.username).one_or_none()
        session.expunge(deck)

        self.active_deck = deck.active_deck
        for card in self.active_deck:
            deck.obtained_cards.remove(card)

        self.remaining_cards = deck.obtained_cards
