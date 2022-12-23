from src.web_server.lib.hallway.cards.card import available_cards
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class AxeSpell(SpellEntity):
    def __init__(self, player):
        card = available_cards["axe"]
        super().__init__(player, card)

        self.animation_sprite_names = [f"axe_{player.direction.value}_{i}" for i in range(4)]
        self.sprite_name = self.animation_sprite_names[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True

