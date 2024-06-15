class Config(object):
    DEBUG = False
    TESTING = False

    # Flask configuration and setup
    HOST = "0.0.0.0"
    PORT = 5000

    SECRET_KEY = (b"\xdf\x1b\x9b\x8a\xf7?\x82\x98\x9f\x10\x05 "
                  b"\xd9\xb4\xdc\xbaz\x8bO\x06\xd6\x8e+y\x9f\x06C\xec\xfd\xfc;_J{\x88^Ht\xf5\xb4")

    SQLALCHEMY_DATABASE_URI = "sqlite:///G:\\OldDDrive\\Projects\\discord-bot\\storage\\database.db"
    # Document storage is required for RAG to index document pages, and we need the raw text for the normal search.


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
