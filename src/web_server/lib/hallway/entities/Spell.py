from src.web_server.lib.hallway.Utils import direction_to_point, Point
from src.web_server.lib.hallway.cards.Card import Card
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity


class SpellEntity(MovableEntity):
    def __init__(self, player, card: Card, unique_identifier: str, game):
        super().__init__(game, unique_identifier)
        self.position = player.position
        self.direction = player.direction if card.ability_range != 0 else None
        self.movement_cooldown = 4
        self.card = card
        self.movement_queue = [direction_to_point(player.direction)] * card.ability_range

        self.sprite_name = self.card.name

        waiting_ticks = max(0, card.animation_length - len(self.movement_queue))
        self.movement_queue.extend([Point(0, 0)] * waiting_ticks)

    def prepare_movement(self):
        pass

    def collide(self, other: Entity) -> bool:
        return True

    def movement_action(self):
        move = super().movement_action()
        # TODO: Check enemy damage

    def post_movement_action(self):
        super().post_movement_action()

        if self.card.damage_type == "heal":
            for player in self.game.player_list:
                dist = player.position.manhattan_distance(self.position)
                if dist <= self.card.radius:
                    player.hp = min(player.max_hp, player.hp + self.card.damage)

        self.die()
