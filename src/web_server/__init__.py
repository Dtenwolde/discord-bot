import os

from flask import Flask
from flask_socketio import SocketIO
import logging
from engineio.payload import Payload

from config import config
from src.database import db
from src import bot
from src.web_server.lib.user_session import session_user

sio = SocketIO(async_mode='gevent')

# Import endpoints to automatically set up routes for SocketIO.
import src.web_server.lib.socket  # noqa
import src.web_server.lib.hallway.socket  # noqa


def create_logger():
    logger = logging.getLogger("timing")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("timing.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)-8s  %(message)s", datefmt="(%H:%M:%S)"))
    logger.addHandler(fh)


def create_app(config_name=None, start_bot=True):
    config_name = os.environ.get(
        "CONFIG", "development" if config_name is None else config_name
    )

    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Set timing logging to file for websocket functions
    create_logger()

    app.jinja_env.globals.update(session_user=session_user)

    Payload.max_decode_packets = 500

    print("Initializing SocketIO")
    sio.init_app(app)
    print("Initializing Database")
    db.init_app(app)
    print("Initializing Bot")
    if start_bot:
        bot.init_app("config.conf", app)

    print("Registering routes")
    from src.web_server import main
    app.register_blueprint(main.bp)

    return app


def cleanup():
    from src.web_server.lib.socket.poker_socket import tables
    for table in tables.values():
        table.cleanup()


def create_models():
    app = create_app(start_bot=False)
    import src.database.models  # noqa
    app.app_context().push()
    drop_first = False
    if drop_first:
        db.drop_all()
    db.create_all()


if __name__ == "__main__":
    create_models()
