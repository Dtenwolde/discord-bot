from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class AxeSpell(SpellEntity):
    card = Card(
        name="axe",
        description="Ooga booga!\nMe Slash!",
        ability_range=5,
        radius=0,
        mana_cost=4,
        damage=7,
        damage_type="prc",
        class_name="AxeSpell"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)

        self.animation_frames = SimpleEntityAnimationFrames([f"axe_{player.direction.value}_{i}" for i in range(4)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True



