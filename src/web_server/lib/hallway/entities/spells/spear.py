from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class SpearSpell(SpellEntity):
    card = Card(
        name="spear",
        description="This spear will stab you!",
        ability_range=10,
        radius=0,
        mana_cost=1,
        damage=1,
        damage_type="prc",
        class_name="SpearSpell"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)
        self.animation_frames = SimpleEntityAnimationFrames([f"spear_{player.direction.value}_{i}" for i in range(2)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True

