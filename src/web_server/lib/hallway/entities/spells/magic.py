from src.web_server.lib.hallway.entities.enemies import EnemyClass
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames, Entity
from src.web_server.lib.hallway.entities.spells import SpellEntity
from src.web_server.lib.hallway.entities.spells.card import Card


class MagicDart(SpellEntity):
    card = Card(
        name="magic dart",
        description="Great description for a great spell",
        ability_range=4,
        radius=0,
        mana_cost=1,
        damage=2,
        damage_type="magic",
        class_name="MagicDart"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)

        self.animation_frames = SimpleEntityAnimationFrames(
            [f"magicdart_{player.direction.value}_{i}" for i in range(3)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True

    def collide(self, other: Entity) -> bool:
        if isinstance(other, EnemyClass):
            self.die()
        return super().collide(other)


class MagicMissile(SpellEntity):
    card = Card(
        name="magic missile",
        description="Upgrade to magic dart",
        ability_range=4,
        radius=0,
        mana_cost=3,
        damage=7,
        damage_type="magic",
        class_name="MagicMissile"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)

        self.animation_frames = SimpleEntityAnimationFrames(
            [f"magicmissile_{player.direction.value}_{i}" for i in range(3)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True

    def collide(self, other: Entity) -> bool:
        if isinstance(other, EnemyClass):
            self.die()
        return super().collide(other)
