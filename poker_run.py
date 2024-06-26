from gevent import monkey

monkey.patch_all()

from geventwebsocket import WebSocketServer

if __name__ == "__main__":
    from src.web_server import create_app, cleanup

    app = create_app()

    from src import bot
    app.secret_key = bot.config["WEBSERVER"]["SECRET"]
    host = bot.config["WEBSERVER"]["IP"]
    port = int(bot.config["WEBSERVER"]["Port"])
    print(f"Spawning webserver on {host}:{port}")
    http_server = WebSocketServer((host, port), app, debug=False)
    try:
        http_server.serve_forever(stop_timeout=1)
    except KeyboardInterrupt:
        cleanup()
        http_server.stop()
