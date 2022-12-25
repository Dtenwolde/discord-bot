import copy
import random

from src.web_server import sio
from src.web_server.lib.hallway.entities.spells import available_cards
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.exceptions import InvalidAction
from src.web_server.lib.hallway.storage.database import db
from src.web_server.lib.hallway.storage.model import StoredDeck


def create_base_deck():
    card_names = []

    # TODO: Remove this debug statement
    [card_names.extend([name] * 10) for name in available_cards.keys()]
    # card_names = ["regeneration"] * 10 + ["axe"] * 10 + ["spear"] * 10
    deck = StoredDeck()
    deck.active_deck = []
    deck.obtained_cards = card_names
    return deck


class Deck:
    """
    A deck is a player-bound class which contains all the cards currently in play.
    It also has a list of all available cards for this specific player.
    The list of available cards for a player will be stored in a database and be consistent across multiple instances.
    """
    MAX_DECK_SIZE = 20
    MAX_HAND_SIZE = 8
    STARTING_HAND_SIZE = 5

    def __init__(self, player):
        from src.web_server.lib.hallway.entities.player_class import PlayerClass
        self.player: PlayerClass = player

        # Active deck and remaining cards are lists of card_names.
        self.selected_cards = []
        self.remaining_cards = []

        self.active_deck = []
        self.hand = []

        self.update_cards_for_player()

    def add_card_to_deck(self, card_name):
        if card_name not in available_cards.keys():
            raise InvalidAction("You tried to add a card which doesn't exist.")

        if len(self.selected_cards) == self.MAX_DECK_SIZE:
            raise InvalidAction(
                f"Your deck already contains the maximum allowed amount ({self.MAX_DECK_SIZE}) of cards.")

        if card_name not in self.remaining_cards:
            raise InvalidAction(f"You do not have any '{card_name}' left.")

        # Remove from remaining cards and add to deck
        self.remaining_cards.remove(card_name)
        self.selected_cards.append(card_name)

    def remove_card_from_deck(self, card_name):
        if card_name not in self.selected_cards:
            raise InvalidAction("You tried to remove a card which was not in your deck.")

        self.selected_cards.remove(card_name)
        self.remaining_cards.append(card_name)

    def play_card(self, idx):
        if 0 <= idx < len(self.hand):
            return self.hand.pop(idx)
        else:
            raise ValueError("Spell attempted which was not in hand.")

    def draw_card(self):
        # Only draw new card when less than 8 are in hand.
        if len(self.hand) != self.MAX_HAND_SIZE:
            self.hand.append(self.active_deck.pop())

    def emit_deck(self):
        data = {
            "max_deck_size": self.MAX_DECK_SIZE,
            "deck_cards": [(
                self.selected_cards.count(card_name),
                available_cards[card_name].to_json()
            ) for card_name in list(dict.fromkeys(self.selected_cards))],
            "remaining_cards": [(
                self.remaining_cards.count(card_name),
                available_cards[card_name].to_json()
            ) for card_name in list(dict.fromkeys(self.remaining_cards))],
        }
        sio.emit("deck", data, json=True,
                 room=self.player.socket, namespace="/hallway")

    def update_cards_for_player(self):
        """
        Gets the currently active deck for a player, and sets the remaining cards based on current deck.
        :return:
        """
        # Fetch data object and remove it from the database session to get a freely editable object
        session = db.session()
        deck = session.query(StoredDeck).filter(StoredDeck.player_name == self.player.username).one_or_none()

        deck = None  # TODO: Remove this debug statement
        if deck is None:
            # Create deck if this is the first time playing
            deck = create_base_deck()
            deck.player_name = self.player.username
            # session.add(deck)
            # session.commit()
        else:
            session.expunge(deck)

        self.selected_cards = deck.active_deck
        for card in self.selected_cards:
            deck.obtained_cards.remove(card)

        self.remaining_cards = deck.obtained_cards

    def start(self):
        self.active_deck = copy.deepcopy(self.selected_cards)
        random.shuffle(self.active_deck)
        self.hand.extend(self.active_deck[:min(self.STARTING_HAND_SIZE, len(self.active_deck))])

    def get_card(self, n_action) -> Card:
        return available_cards[self.hand[n_action]]
