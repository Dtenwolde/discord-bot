from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames, Entity
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity
from src.web_server.lib.hallway.exceptions import InvalidAction


class PoisonDart(SpellEntity):
    card = Card(
        name="poison dart",
        description="Deals 8 damage over time.",
        ability_range=99,
        radius=0,
        mana_cost=1,
        damage=0,
        damage_type="prc",
        class_name="PoisonDart"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)
        self.animation_frames = SimpleEntityAnimationFrames([f"poisondart_{player.direction.value}_0"])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 80
        self.movement_cooldown = 4
        self.animating = True
        self.loop = True

    def movement_action(self):
        try:
            return super().movement_action()
        except InvalidAction as e:
            self.die()

    def collide(self, other: Entity) -> bool:
        # TODO: Fix circular import with enemyclass here.
        from src.web_server.lib.hallway.entities.enemies import EnemyClass

        if isinstance(other, EnemyClass):
            passive = Passive(other, time=8)
            passive.mods.hp_regen = -1
            other.passives.append(passive)
            self.die()

        return super().collide(other)
