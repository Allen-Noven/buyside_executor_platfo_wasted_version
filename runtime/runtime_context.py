# ====================================
# runtime_context.py
# ====================================

from utils.logger import (
    SystemLogger
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# RUNTIME OBJECTS
# ====================================

market_state = None

redis_state = None

event_bus = None

oms = None

position_manager = None

execution_service = None

order_queue = None

execution_worker = None


# ====================================
# RUNTIME STATUS
# ====================================

runtime_status = {

    "initialized":
    False,

    "worker_running":
    False
}


# ====================================
# REGISTER RUNTIME
# ====================================

def register_runtime(

    runtime_market_state=None,

    runtime_redis_state=None,

    runtime_event_bus=None,

    runtime_oms=None,

    runtime_position_manager=None,

    runtime_execution_service=None,

    runtime_order_queue=None,

    runtime_execution_worker=None
):

    global market_state

    global redis_state

    global event_bus

    global oms

    global position_manager

    global execution_service

    global order_queue

    global execution_worker

    market_state = (
        runtime_market_state
    )

    redis_state = (
        runtime_redis_state
    )

    event_bus = (
        runtime_event_bus
    )

    oms = (
        runtime_oms
    )

    position_manager = (
        runtime_position_manager
    )

    execution_service = (
        runtime_execution_service
    )

    order_queue = (
        runtime_order_queue
    )

    execution_worker = (
        runtime_execution_worker
    )

    runtime_status[
        "initialized"
    ] = True

    logger.info(
        "Runtime Registered"
    )


# ====================================
# UPDATE WORKER STATUS
# ====================================

def set_worker_running(

    is_running
):

    runtime_status[
        "worker_running"
    ] = is_running

    logger.info(

        f"Worker Running = "

        f"{is_running}"
    )


# ====================================
# GET RUNTIME STATUS
# ====================================

def get_runtime_status():

    return {

        "initialized":
        runtime_status["initialized"],

        "worker_running":
        runtime_status["worker_running"],

        "has_market_state":
        market_state is not None,

        "has_event_bus":
        event_bus is not None,

        "has_oms":
        oms is not None,

        "has_execution_service":
        execution_service is not None,

        "has_execution_worker":
        execution_worker is not None
    }


# ====================================
# SHOW RUNTIME STATUS
# ====================================

def show_runtime_status():

    status = (
        get_runtime_status()
    )

    print(

        "\n========== RUNTIME STATUS ==========\n"
    )

    for key, value in status.items():

        print(f"{key}: {value}")

    print(

        "\n====================================\n"
    )