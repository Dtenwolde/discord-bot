import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


class Database:
    def __init__(self, name: str):
        self.engine = sqlalchemy.create_engine('sqlite:///' + name, echo=False)
        self.connection = self.engine.connect()
        self._session_factory = sessionmaker(autocommit=False, autoflush=True, bind=self.engine)
        self._session = scoped_session(self._session_factory)

    def session(self) -> scoped_session:
        return self._session()

    def set_config(self, name):
        self.config.read(name)


def create_all_models():
    GameBase.metadata.create_all(db.engine)


# Create db
GameBase = declarative_base()
db = Database("src/web_server/lib/hallway/storage/database.db")
