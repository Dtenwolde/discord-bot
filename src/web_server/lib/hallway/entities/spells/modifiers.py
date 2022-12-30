from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells import SpellEntity
from src.web_server.lib.hallway.entities.spells.card import Card


class Anger(SpellEntity):
    card = Card(
        name="anger",
        description="This will increase your spells' damage by 3 for 4 turns",
        ability_range=0,
        radius=0,
        mana_cost=3,
        damage=3,
        damage_type="heal",
        class_name="Anger"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1, 2, 3, 4]]

        super().__init__(player, animation_length=len(frames))

        self.animation_frames = SimpleEntityAnimationFrames(frames)
        self.animation_zoom = [1, 1, 1, 1, 1]

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 5
        self.animating = True
        self.loop = False

        passive = Passive(player, time=4, name="Anger")
        passive.mods.dma = self.card.damage

        player.passives.append(passive)


class Sharpen(SpellEntity):
    card = Card(
        name="sharpen",
        description="Sharpen your tools. Multiply piercing damage by 2 for 5 turns.",
        ability_range=0,
        radius=0,
        mana_cost=3,
        damage=0,
        damage_type="heal",
        class_name="Sharpen"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1, 2, 3, 4]]

        super().__init__(player, animation_length=len(frames))

        self.animation_frames = SimpleEntityAnimationFrames(frames)
        self.animation_zoom = [1, 1, 1, 1, 1]

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 5
        self.animating = True
        self.loop = False

        passive = Passive(player, time=5, name="Sharpen")
        passive.mods.dmm = 2
        passive.mods.dm_restriction = "prc"

        player.passives.append(passive)


class Fastcasting(SpellEntity):
    card = Card(
        name="fastcasting",
        description="Channel magic energy to reduce the required mana per spell by 1 for the next 3 turns.",
        ability_range=0,
        radius=0,
        mana_cost=1,
        damage=0,
        damage_type="heal",
        class_name="Fastcasting"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1, 2]]

        super().__init__(player, animation_length=len(frames))

        self.animation_frames = SimpleEntityAnimationFrames(frames)
        self.animation_zoom = [1, 1, 1]
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 5
        self.animating = True
        self.loop = False

        passive = Passive(player, time=5, name="Fastcasting")
        passive.mods.spell_cost_reduction = 1
        player.passives.append(passive)
