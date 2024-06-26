from src.database.models import models
from src.database.repository import profile_repository


class Player:
    """
        Stores information about a player participating in a web_server game.
    """

    def __init__(self, profile: models.UserModel, socket, table):
        self.profile = profile
        self.socket = socket
        self.initial_balance = profile.balance

        from src.web_server.lib.poker.PokerTable import PokerTable
        self.table: PokerTable = table

        self.ready = False

        self.hand = []
        self.all_in = False

        self.current_call_value = 0

    def deal(self, cards):
        self.hand.append(cards)

    def reset(self):
        self.hand = []
        self.all_in = False
        self.current_call_value = 0

    def pay(self, current_call_value):
        """
        :param current_call_value:
        :return:
        """
        to_pay = current_call_value - self.current_call_value

        if self.profile['balance'] <= to_pay:  # all in
            paid = self.profile['balance']
            self.profile['balance'] = 0
            self.all_in = True

            self.table.broadcast("%s went all in." % self.profile['owner'])
            self.table.all_in_list.append(self)
        else:  # not all in
            paid = to_pay
            self.profile = profile_repository.update_money(self.profile, -to_pay)
        self.current_call_value = current_call_value
        return paid

    def payout(self, pot):
        self.profile = profile_repository.update_money(self.profile, pot)

    def export_hand(self):
        if len(self.hand) == 0:
            return None
        return [card.to_json() for card in self.hand]

    def leave(self):
        # TODO
        """
        Call this function if the player leaves the table.
        This will return the chips back to the user.

        :return:
        """

        pass
        # self.user.set_chips(self.chips)
        # self.chips = None
