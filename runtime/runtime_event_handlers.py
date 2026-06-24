# ====================================
# runtime_event_handlers.py
# ====================================

import asyncio

from api.execution_api import (
    broadcast_event
)


# ====================================
# SYSTEM ERROR HANDLER
# ====================================

def websocket_broadcast_handler(

    payload
):

    asyncio.run(

        broadcast_event(

            "SYSTEM_ERROR",

            payload
        )
    )