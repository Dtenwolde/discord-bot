from src.web_server.lib.hallway.cards.card import available_cards
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class HealSpell(SpellEntity):
    def __init__(self, player):
        card = available_cards["heal"]
        super().__init__(player, card)

    def post_movement_action(self):
        if self.card.damage_type == "heal":
            for player in self.game.player_list:
                dist = player.position.manhattan_distance(self.position)
                if dist <= self.card.radius:
                    player.hp = min(player.max_hp, player.hp + self.card.damage)

        super().post_movement_action()
