from src.web_server.lib.hallway.algorithms import pathfinding
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class Axe(SpellEntity):
    card = Card(
        name="axe",
        description="Ooga booga!\nMe Slash!",
        ability_range=5,
        radius=0,
        mana_cost=4,
        damage=7,
        damage_type="prc",
        class_name="Axe"
                   ""
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)

        self.animation_frames = SimpleEntityAnimationFrames([f"axe_{player.direction.value}_{i}" for i in range(4)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True


class Spear(SpellEntity):
    card = Card(
        name="spear",
        description="This spear will stab you!",
        ability_range=10,
        radius=0,
        mana_cost=1,
        damage=1,
        damage_type="prc",
        class_name="Spear"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)
        self.animation_frames = SimpleEntityAnimationFrames([f"spear_{player.direction.value}_{i}" for i in range(2)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True


class Boomerang(SpellEntity):
    card = Card(
        name="boomerang",
        description="Forth....... and back.",
        ability_range=3,
        radius=0,
        mana_cost=1,
        damage=2,
        damage_type="prc",
        class_name="Boomerang"
    )

    def __init__(self, player):
        super().__init__(player, animation_length=self.card.ability_range)
        self.animation_frames = SimpleEntityAnimationFrames([f"boomerang_{player.direction.value}_{i}" for i in range(2)])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = True

        self.player = player
        self.returning = False

    def post_movement_action(self):
        if self.returning:
            super().post_movement_action()
        else:
            self.returning = True

    def before_turn_action(self):
        if self.returning:
            self.movement_queue = pathfinding.astar(self.game.board, self.position, self.player.position)
