from aiohttp import web, WSMsgType, WSCloseCode
import weakref
from typing import Any, Callable


# store websockets
# https://docs.aiohttp.org/en/stable/web_advanced.html#websocket-shutdown
websockets = web.AppKey("websockets", weakref.WeakSet)

socket_msg_handler = web.AppKey("socket_msg_handler", Callable)


async def status():
    return web.Response(text="OK")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app[websockets].add(ws)

    handler = request.app[socket_msg_handler]
    socket_ctx = handler.create_per_socket_ctx()

    async def ws_send_json(data: Any):
        await ws.send_json((data))

    try:
        async for msg in ws:
            # print("RAW MSG:", msg)
            if msg.type == WSMsgType.TEXT:
                if handler:
                    msg = msg.json()
                    await handler(socket_ctx, msg, ws_send_json)
            elif msg.type == WSMsgType.ERROR:
                print("ws connection closed with exception %s" % ws.exception())
    finally:
        request.app[websockets].discard(ws)
    print("websocket connection closed")

    return ws


async def index_handler(_request):
    raise web.HTTPFound(location="/index.html")


async def on_shutdown(app):
    for ws in set(app[websockets]):
        await ws.close(code=WSCloseCode.GOING_AWAY, message="Server shutdown")


def create_server(static_dir):
    app = web.Application()

    app[websockets] = weakref.WeakSet()
    app.on_shutdown.append(on_shutdown)

    app.add_routes([web.get("/status", status)])
    app.add_routes([web.get("/ws", websocket_handler)])
    app.add_routes([web.get("/", index_handler)])

    # bleh, bleh, development only (aiohttp docs mumbling continues..)
    app.add_routes([web.static("/", static_dir)])

    return app


def set_socket_msg_handler(app, handler):
    app[socket_msg_handler] = handler


def debug_print_sockets(msg):
    print("SOCKET RCV:", msg)
    resp = {"bar": ("baz", None, 1.0, 2)}
    return resp


def start_server(app):
    web.run_app(app, host="localhost")


if __name__ == "__main__":
    import os

    cwd = os.getcwd()
    static_dir = os.path.join(cwd, "static")

    app = create_server(static_dir)

    set_socket_msg_handler(app, debug_print_sockets)

    print("http://localhost:8080/index.html")
    start_server(app)
