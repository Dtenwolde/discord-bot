from typing import Type


class DamageTypes:
    PIERCING = 0
    HEALING = 1
    FIRE = 2

    @staticmethod
    def from_txt(txt):
        lookup = {
            "prc": DamageTypes.PIERCING,
            "heal": DamageTypes.HEALING,
            "fire": DamageTypes.FIRE,
        }
        return lookup[txt]


class Card:
    def __init__(self, name, description, ability_range, radius, mana_cost, damage, damage_type: str, class_name):
        super().__init__()
        self.name = name
        self.description = description
        self.ability_range = ability_range
        self.radius = radius
        self.mana_cost = mana_cost
        self.damage = damage
        self.damage_type = damage_type
        self.class_name = class_name

    def create_object(self, player):
        # Import this to ensure we have loaded all spells
        from src.web_server.lib.hallway.entities.spells.spell import SpellEntity
        cls = None  # noqa
        for sub_cls in SpellEntity.__subclasses__():
            if sub_cls.__name__ == self.class_name:
                cls = sub_cls

        if cls is None:
            raise AssertionError(f"Attempted to create object for which no class is defined: '{self.class_name}'.")
        cls: Type[SpellEntity]
        return cls(player)

    def to_json(self):
        return vars(self)
