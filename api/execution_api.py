# ====================================
# execution_api.py
# ====================================

from fastapi import (
    FastAPI,
    WebSocket
)

from pydantic import (
    BaseModel
)

from utils.logger import (
    SystemLogger
)

from utils.runtime_mode import (
    RUNTIME_MODE
)

from core.parent_order import (
    ParentOrder
)

import runtime.runtime_context as runtime_context


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)

logger.warning(
    f"FASTAPI Runtime Mode | {RUNTIME_MODE}"
)


# ====================================
# FASTAPI APP
# ====================================

app = FastAPI()


# ====================================
# WEBSOCKET CONNECTIONS
# ====================================

active_connections = []


# ====================================
# ORDER REQUEST MODEL
# ====================================

class OrderRequest(BaseModel):

    symbol: str

    qty: float

    side: str


# ====================================
# GET EXECUTION SERVICE
# ====================================

def get_execution_service():

    service = (
        runtime_context.execution_service
    )

    if service is None:

        raise RuntimeError(
            "ExecutionService Not Initialized"
        )

    return service


# ====================================
# HEALTH CHECK
# ====================================

@app.get("/health")
def health():

    return {

        "status":
        "running",

        "runtime_mode":
        RUNTIME_MODE,

        "runtime_initialized":
        runtime_context.runtime_status[
            "initialized"
        ],

        "has_execution_service":
        runtime_context.execution_service is not None,

        "has_position_manager":
        runtime_context.position_manager is not None,

        "worker_running":
        runtime_context.runtime_status[
            "worker_running"
        ]
    }


# ====================================
# WEBSOCKET
# ====================================

@app.websocket("/ws")
async def websocket_endpoint(

    websocket: WebSocket
):

    await websocket.accept()

    active_connections.append(
        websocket
    )

    logger.info(
        "WebSocket Client Connected"
    )

    try:

        while True:

            await websocket.receive_text()

    except Exception:

        if websocket in active_connections:

            active_connections.remove(
                websocket
            )

        logger.warning(
            "WebSocket Client Disconnected"
        )


# ====================================
# BROADCAST EVENT
# ====================================

async def broadcast_event(

    event,

    payload
):

    message = {

        "event":
        event,

        "payload":
        payload
    }

    disconnected = []

    for connection in active_connections:

        try:

            await connection.send_json(
                message
            )

        except Exception:

            disconnected.append(
                connection
            )

    for connection in disconnected:

        if connection in active_connections:

            active_connections.remove(
                connection
            )


# ====================================
# SUBMIT ORDER
# ====================================

@app.post("/orders")
async def submit_order(

    order: OrderRequest
):

    logger.info(

        f"External PM Order | "
        f"{order.symbol} | "
        f"{order.qty}"
    )

    try:

        execution_service = (
            get_execution_service()
        )

        parent_order = (

            ParentOrder(

                symbol=
                order.symbol,

                side=
                order.side,

                quantity=
                order.qty,

                strategy=
                "VWAP"
            )
        )

        result = (

            execution_service.submit_order(
                parent_order
            )
        )

        await broadcast_event(

            "ORDER_UPDATE",

            {

                "symbol":
                order.symbol,

                "qty":
                order.qty,

                "side":
                order.side,

                "status":
                result.get(
                    "status",
                    "UNKNOWN"
                ),

                "order_id":
                result.get(
                    "order_id"
                )
            }
        )

        await broadcast_event(

            "EXECUTION_COMPLETED",

            {

                "symbol":
                order.symbol,

                "qty":
                order.qty,

                "side":
                order.side
            }
        )

        return {

            "accepted":
            True,

            "symbol":
            order.symbol,

            "qty":
            order.qty,

            "side":
            order.side,

            "result":
            result
        }

    except Exception as error:

        logger.error(

            f"Execution API Failed | "
            f"{error}"
        )

        await broadcast_event(

            "SYSTEM_ERROR",

            {

                "source":
                "ExecutionAPI",

                "message":
                str(error)
            }
        )

        return {

            "accepted":
            False,

            "error":
            str(error)
        }


# ====================================
# GET POSITIONS
# ====================================

@app.get("/positions")
def get_positions():

    if runtime_context.position_manager is None:

        return {}

    return (

        runtime_context
        .position_manager
        .get_all_positions()
    )


# ====================================
# GET ACTIVE ORDERS
# ====================================

@app.get("/active-orders")
def get_active_orders():

    execution_service = (
        get_execution_service()
    )

    return (

        execution_service
        .get_active_orders()
    )


# ====================================
# GET PORTFOLIO
# ====================================

@app.get("/portfolio")
def get_portfolio():

    if runtime_context.position_manager is None:

        return {

            "total_realized_pnl":
            0,

            "total_unrealized_pnl":
            0,

            "total_exposure":
            0,

            "position_count":
            0
        }

    return (

        runtime_context
        .position_manager
        .get_portfolio_summary()
    )