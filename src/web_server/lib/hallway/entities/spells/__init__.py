from src.web_server.lib.hallway.entities.spells.spell import SpellEntity
import src.web_server.lib.hallway.entities.spells.heal
import src.web_server.lib.hallway.entities.spells.fire
import src.web_server.lib.hallway.entities.spells.modifiers
import src.web_server.lib.hallway.entities.spells.piercing
import src.web_server.lib.hallway.entities.spells.poison
import src.web_server.lib.hallway.entities.spells.force

available_cards = {cls.card.name: cls.card for cls in SpellEntity.__subclasses__()}

print(available_cards.keys())
