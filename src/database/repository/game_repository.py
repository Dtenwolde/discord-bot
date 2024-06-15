from src.database import db
from src.database.models.models import LeagueGame


def get_match_by_id(match_id):
    session = db.session
    return session.query(LeagueGame).filter(LeagueGame.game_id == match_id).all()
