# ====================================
# websocket_api.py
# ====================================

from fastapi import (

    FastAPI,

    WebSocket,

    WebSocketDisconnect
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)

from runtime.runtime_context import (
    event_bus
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# FASTAPI APP
# ====================================

app = FastAPI(

    title="Execution Platform WebSocket API"
)


# ====================================
# CONNECTION MANAGER
# ====================================

class ConnectionManager:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.active_connections = []

        logger.info(
            "WebSocket Manager Initialized"
        )


    # ====================================
    # CONNECT
    # ====================================

    async def connect(

        self,

        websocket: WebSocket
    ):

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

        logger.info(

            f"WebSocket Connected | "

            f"Clients: "

            f"{len(self.active_connections)}"
        )


    # ====================================
    # DISCONNECT
    # ====================================

    def disconnect(

        self,

        websocket: WebSocket
    ):

        if websocket in self.active_connections:

            self.active_connections.remove(
                websocket
            )

        logger.warning(

            f"WebSocket Disconnected | "

            f"Clients: "

            f"{len(self.active_connections)}"
        )


    # ====================================
    # SEND MESSAGE
    # ====================================

    async def send_message(

        self,

        message: dict
    ):

        disconnected_clients = []

        for connection in self.active_connections:

            try:

                await connection.send_json(
                    message
                )

            except Exception as error:

                logger.error(

                    f"WebSocket Send Failed | "

                    f"{error}"
                )

                disconnected_clients.append(
                    connection
                )

        # ====================================
        # CLEANUP
        # ====================================

        for client in disconnected_clients:

            self.disconnect(client)


    # ====================================
    # BROADCAST EVENT
    # ====================================

    async def broadcast_event(

        self,

        event_type,

        payload
    ):

        message = {

            "event":
            event_type,

            "timestamp":
            get_current_timestamp(),

            "payload":
            payload
        }

        await self.send_message(
            message
        )


# ====================================
# MANAGER
# ====================================

manager = (
    ConnectionManager()
)


# ====================================
# EVENT HANDLERS
# ====================================

async def handle_market_update(
    payload
):

    await manager.broadcast_event(

        "MARKET_UPDATE",

        payload
    )


async def handle_order_update(
    payload
):

    await manager.broadcast_event(

        "ORDER_UPDATE",

        payload
    )


async def handle_fill_update(
    payload
):

    await manager.broadcast_event(

        "FILL_UPDATE",

        payload
    )


async def handle_position_update(
    payload
):

    await manager.broadcast_event(

        "POSITION_UPDATE",

        payload
    )


async def handle_risk_alert(
    payload
):

    await manager.broadcast_event(

        "RISK_ALERT",

        payload
    )


# ====================================
# EVENT SUBSCRIPTIONS
# ====================================

event_bus.subscribe(

    "MARKET_UPDATE",

    handle_market_update
)

event_bus.subscribe(

    "ORDER_UPDATE",

    handle_order_update
)

event_bus.subscribe(

    "FILL_UPDATE",

    handle_fill_update
)

event_bus.subscribe(

    "POSITION_UPDATE",

    handle_position_update
)

event_bus.subscribe(

    "RISK_ALERT",

    handle_risk_alert
)


# ====================================
# WEBSOCKET ENDPOINT
# ====================================

@app.websocket("/ws")

async def websocket_endpoint(

    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )

    except Exception as error:

        logger.error(

            f"WebSocket Error | "

            f"{error}"
        )

        manager.disconnect(
            websocket
        )


# ====================================
# HEALTH CHECK
# ====================================

@app.get("/health")

def health_check():

    return {

        "status":
        "RUNNING",

        "active_connections":

        len(manager.active_connections)
    }