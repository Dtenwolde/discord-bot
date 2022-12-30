import copy
import uuid

from src.web_server.lib.hallway.Utils import EntityDirections, direction_to_point, Point
from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames, Entity
from src.web_server.lib.hallway.entities.spells import SpellEntity
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.exceptions import InvalidAction


class Force(SpellEntity):
    card = Card(
        name="force",
        description="Forces enemies within a 3-wide line to be pushed back.",
        ability_range=5,
        radius=0,
        mana_cost=3,
        damage=0,
        damage_type="heal",
        class_name="Force"
    )

    def __init__(self, player):
        frames = [f"force_{player.direction.value}_{i}" for i in [0, 1]]

        super().__init__(player, animation_length=len(frames))

        self.animation_frames = SimpleEntityAnimationFrames(frames)

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 10
        self.animating = True
        self.loop = False

        assert self.direction is not None

        # Create left and right flank for the spell
        left = copy.copy(self)
        left.movement_queue = copy.copy(self.movement_queue)
        left.uid = str(uuid.uuid4())
        left.position += direction_to_point(EntityDirections.rotate(self.direction, 90))
        right = copy.copy(self)
        right.movement_queue = copy.copy(self.movement_queue)
        right.uid = str(uuid.uuid4())
        right.position += direction_to_point(EntityDirections.rotate(self.direction, 270))

        self.entities.extend([left, right])

    def movement_action(self):
        try:
            super().movement_action()
        except InvalidAction as e:
            self.die()

    def collide(self, other: Entity) -> bool:
        from src.web_server.lib.hallway.entities.enemies import EnemyClass
        if isinstance(other, EnemyClass):
            # Add my own movement to the entities which are to be pushed back
            other.movement_queue.extend(self.movement_queue)
            other.movement_cooldown = self.movement_cooldown

        return True


class Teleport(SpellEntity):
    card = Card(
        name="teleport",
        description="Teleports self 3 spaces forward.",
        ability_range=3,
        radius=0,
        mana_cost=1,
        damage=0,
        damage_type="heal",
        class_name="Teleport"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1]]

        super().__init__(player, animation_length=len(frames))
        self.movement_queue = [Point(0, 0)] * len(frames)
        self.animation_frames = SimpleEntityAnimationFrames(frames)

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 5
        self.animating = True
        self.loop = False

        increment = direction_to_point(player.direction)
        for i in range(self.card.ability_range):
            new_position = player.position + increment
            if player.game.board[new_position.x][new_position.y].movement_allowed:
                player.position += increment

        # We moved, so update sight
        player.update_line_of_sight()


class Haste(SpellEntity):
    card = Card(
        name="haste",
        description="Grants 2 more movement speed for 3 turns.",
        ability_range=0,
        radius=0,
        mana_cost=3,
        damage=0,
        damage_type="heal",
        class_name="Haste"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1]]

        super().__init__(player, animation_length=len(frames))
        self.animation_frames = SimpleEntityAnimationFrames(frames)

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 5
        self.animating = True
        self.loop = False

        def reduce():
            player.MAX_MOVEMENT -= 2

        player.MAX_MOVEMENT += 2
        passive = Passive(player, time=3, name="Haste buff")
        passive.callback = reduce

        player.passives.append(passive)
