import uuid


class PassiveModifiers(object):
    def __init__(self):
        self.dmm = 1  # Damage multiplier multiplicative
        self.dma = 0  # Damage multiplier additive
        self.dm_restriction = None  # Damage modifier restriction.
        self.mana_regen = 0
        self.hp_regen = 0
        self.temp_hp = 0


class Passive(object):
    def __init__(self, player, time, name="", callback=None, args=()):
        from src.web_server.lib.hallway.entities.player_class import PlayerClass
        self.uid = str(uuid.uuid4())
        self.name = name
        self.total_time = time
        self.time = time
        self.player: PlayerClass = player

        self.callback = callback
        self.args = args

        self.mods = PassiveModifiers()

    def tick(self):
        self.player.mana += self.mods.mana_regen
        self.player.hp += self.mods.hp_regen

        self.time -= 1
        if self.time == 0:
            if self.callback is not None:
                self.callback(*self.args)

    def damage_mod_multiplicative(self, dmg, dmg_type):
        if self.mods.dm_restriction is None or self.mods.dm_restriction == dmg_type:
            return dmg * self.mods.dmm
        return dmg

    def damage_mod_additive(self, dmg, dmg_type):
        if self.mods.dm_restriction is None or self.mods.dm_restriction == dmg_type:
            return dmg + self.mods.dma
        return dmg

    def to_json(self):
        """
        Converts the passive to json, maybe for later to display all active passives

        :return:
        """
        return {
            "uid": self.uid,
            "name": self.name,
            "time": self.time,
            "total_time": self.total_time,
        }


class HPRegeneration(Passive):
    def __init__(self, player, time, regen_mod):
        super().__init__(player, time, "HP Regen")
        self.mods.hp_regen = regen_mod
