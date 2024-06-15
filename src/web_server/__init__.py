import os

from flask import Flask
from flask_socketio import SocketIO
import logging
from engineio.payload import Payload

from config import config
from database import db
from src.web_server.lib.user_session import session_user

sio = SocketIO(async_mode='gevent')

# Import endpoints to automatically set up routes for SocketIO.
import src.web_server.lib.socket  # noqa


def create_logger():
    logger = logging.getLogger("timing")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("timing.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)-8s  %(message)s", datefmt="(%H:%M:%S)"))
    logger.addHandler(fh)


def create_app(config_name=None):
    config_name = os.environ.get(
        "CONFIG", "development" if config_name is None else config_name
    )

    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Set timing logging to file for websocket functions
    create_logger()

    app.jinja_env.globals.update(session_user=session_user)

    print("Created socketio")
    Payload.max_decode_packets = 500

    sio.init_app(app)

    import src.database.models.models  # noqa
    app.app_context().push()
    db.init_app(app)
    drop_first = False
    if drop_first:
        db.drop_all()
    db.create_all()


    from src.web_server import main
    app.register_blueprint(main.bp)

    return app


def cleanup():
    from src.web_server.lib.socket.poker_socket import tables
    for table in tables.values():
        table.cleanup()
