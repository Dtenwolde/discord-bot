from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class Fireball(SpellEntity):
    card = Card(
        name="fireball",
        description="You know what this does.",
        ability_range=7,
        radius=3,
        mana_cost=4,
        damage=3,
        damage_type="fire",
        class_name="Fireball"
    )

    def __init__(self, player):
        line_sprites = [0, 1] * ((self.card.ability_range + 1) // 2)
        explode_sprites = [2, 3, 4]
        sprites = line_sprites[:self.card.ability_range] + explode_sprites
        frames = [f"fireball_{player.direction.value}_{i}" for i in sprites]

        super().__init__(player, animation_length=len(frames))
        self.animation_frames = SimpleEntityAnimationFrames(frames)
        self.animation_zoom = [1] * 7 + [1, 2, 3]

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.movement_cooldown = self.frame_duration = 4  # Synchronize movement with animation
        self.animating = True
        self.loop = False

    def post_movement_action(self):
        from src.web_server.lib.hallway.entities.enemies import EnemyClass
        for enemy in [e for e in self.game.enemy_entities if isinstance(e, EnemyClass)] + self.game.player_list:
            dist = enemy.position.manhattan_distance(self.position)
            if dist <= self.card.radius:
                enemy.hp -= self.card.damage

        super().post_movement_action()
