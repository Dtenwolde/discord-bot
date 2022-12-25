from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class HealSpell(SpellEntity):
    card = Card(
        name="heal",
        description="This will heal you and all allies within 3 squares of yourself.",
        ability_range=0,
        radius=3,
        mana_cost=3,
        damage=5,
        damage_type="heal",
        class_name="HealSpell"
    )

    def __init__(self, player):
        frames = [f"heal_{i}" for i in [0, 1, 2, 3, 4, 4]]

        super().__init__(player, animation_length=len(frames))

        self.animation_frames = SimpleEntityAnimationFrames(frames)
        self.animation_zoom = [1, 1, 1, 2, 3, 4]

        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.frame_duration = 4
        self.animating = True
        self.loop = False

    def post_movement_action(self):
        if self.card.damage_type == "heal":
            for player in self.game.player_list:
                dist = player.position.manhattan_distance(self.position)
                if dist <= self.card.radius:
                    player.hp = min(player.max_hp, player.hp + self.card.damage)

        super().post_movement_action()


class RegenerationSpell(SpellEntity):
    card = Card(
        name="regeneration",
        description="This will heal you for 3 hp after every move for 4 moves.",
        ability_range=0,
        radius=0,
        mana_cost=3,
        damage=3,
        damage_type="heal",
        class_name="RegenerationSpell"
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

        regen_passive = Passive(player, 4, "Regeneration")
        regen_passive.mods.hp_regen = self.card.damage

        player.passives.append(regen_passive)
