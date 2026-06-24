# ====================================
# runtime_bootstrap.py
# ====================================

import threading

from utils.logger import (
    SystemLogger
)

from utils.runtime_mode import (

    RUNTIME_MODE,

    SIMULATION,

    PAPER,

    LIVE
)

from runtime.runtime_context import (
    register_runtime,
    set_worker_running
)

from core.market_state import (
    MarketState
)

from core.redis_state import (
    RedisState
)

from data.market_event_bus import (
    MarketEventBus
)

from data.fake_market_generator import (
    SimulationMarketGenerator
)

from execution.order_queue import (
    OrderQueue
)

from execution.execution_service import (
    ExecutionService
)

from execution.execution_worker import (
    ExecutionWorker
)

from execution.oms.oms_factory import (
    create_oms
)

from portfolio.position_manager import (
    PositionManager
)

from portfolio.broker_position_service import (
    BrokerPositionService
)

from portfolio.position_reconciliation import (
    PositionReconciliation
)

from portfolio.reconciliation_worker import (
    ReconciliationWorker
)

from storage.order_repository import (
    OrderRepository
)

from storage.position_repository import (
    PositionRepository
)

from runtime.runtime_event_handlers import (
    websocket_broadcast_handler
)


class RuntimeBootstrap:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.order_repository = (
            OrderRepository()
        )

        self.position_repository = (
            PositionRepository()
        )

        self.market_generator = None

        self.market_state = None

        self.redis_state = None

        self.event_bus = None

        self.oms = None

        self.position_manager = None

        self.broker_position_service = None

        self.position_reconciliation = None

        self.reconciliation_worker = None

        self.execution_service = None

        self.order_queue = None

        self.execution_worker = None

        self.execution_worker_thread = None


    # ====================================
    # BOOTSTRAP
    # ====================================

    def bootstrap(self):

        self.logger.warning(

            f"Bootstrapping Runtime | "

            f"Mode={RUNTIME_MODE}"
        )

        try:

            # ====================================
            # CORE RUNTIME
            # ====================================

            self.market_state = (
                MarketState()
            )

            self.redis_state = (
                RedisState()
            )

            # ====================================
            # EVENT BUS
            # ====================================

            self.event_bus = (
                MarketEventBus()
            )

            # ====================================
            # EVENT SUBSCRIPTIONS
            # ====================================

            self.event_bus.subscribe(

                "SYSTEM_ERROR",

                websocket_broadcast_handler
            )

            self.logger.info(
                "SYSTEM_ERROR Handler Registered"
            )

            # ====================================
            # POSITION MANAGER
            # ====================================

            self.position_manager = (

                PositionManager(

                    event_bus=
                    self.event_bus
                )
            )

            # ====================================
            # OMS
            # ====================================

            self.oms = (
                create_oms()
            )

            # ====================================
            # MARKET GENERATOR
            # ====================================

            if RUNTIME_MODE == SIMULATION:

                self.market_generator = (

                    SimulationMarketGenerator(

                        market_state=
                        self.market_state,

                        event_bus=
                        self.event_bus
                    )
                )

                self.logger.info(
                    "Simulation Market Generator Created"
                )

            # ====================================
            # BROKER POSITION / RECONCILIATION
            # ====================================

            if RUNTIME_MODE in [

                PAPER,

                LIVE
            ]:

                self.broker_position_service = (

                    BrokerPositionService(

                        event_bus=
                        self.event_bus
                    )
                )

                self.position_reconciliation = (

                    PositionReconciliation(

                        internal_position_manager=
                        self.position_manager,

                        broker_positions=
                        self.broker_position_service,

                        event_bus=
                        self.event_bus
                    )
                )

                self.reconciliation_worker = (

                    ReconciliationWorker(

                        broker_position_service=
                        self.broker_position_service,

                        reconciliation_engine=
                        self.position_reconciliation,

                        interval=30
                    )
                )

                self.logger.info(
                    "Broker Position Reconciliation Created"
                )

            else:

                self.logger.warning(

                    "Broker Reconciliation Disabled "
                    "For Simulation Runtime"
                )

            # ====================================
            # EXECUTION SERVICE
            # ====================================

            self.execution_service = (

                ExecutionService(

                    market_state=
                    self.market_state,

                    event_bus=
                    self.event_bus,

                    oms=
                    self.oms,

                    position_manager=
                    self.position_manager
                )
            )

            # ====================================
            # ORDER QUEUE
            # ====================================

            self.order_queue = (
                OrderQueue()
            )

            # ====================================
            # EXECUTION WORKER
            # ====================================

            self.execution_worker = (

                ExecutionWorker(

                    order_queue=
                    self.order_queue,

                    execution_service=
                    self.execution_service
                )
            )

            # ====================================
            # REGISTER RUNTIME
            # ====================================

            register_runtime(

                runtime_market_state=
                self.market_state,

                runtime_redis_state=
                self.redis_state,

                runtime_event_bus=
                self.event_bus,

                runtime_oms=
                self.oms,

                runtime_position_manager=
                self.position_manager,

                runtime_execution_service=
                self.execution_service,

                runtime_order_queue=
                self.order_queue,

                runtime_execution_worker=
                self.execution_worker
            )

            # ====================================
            # RECOVER STATE
            # ====================================

            self.recover_runtime_state()

            # ====================================
            # START WORKER
            # ====================================

            self.start_execution_worker()

            # ====================================
            # START MARKET GENERATOR
            # ====================================

            if self.market_generator:

                self.market_generator.start_async()

            # ====================================
            # START RECONCILIATION WORKER
            # ====================================

            if self.reconciliation_worker:

                self.reconciliation_worker.start()

            self.logger.info(
                "Runtime Bootstrap Complete"
            )

        except Exception as error:

            self.logger.error(

                f"Runtime Bootstrap Failed | "

                f"{error}"
            )

            raise


    # ====================================
    # START EXECUTION WORKER
    # ====================================

    def start_execution_worker(self):

        try:

            if self.execution_worker is None:

                raise RuntimeError(
                    "Execution Worker Not Initialized"
                )

            self.execution_worker_thread = threading.Thread(

                target=
                self.execution_worker.start,

                daemon=True
            )

            self.execution_worker_thread.start()

            set_worker_running(True)

            self.logger.info(
                "Execution Worker Thread Started"
            )

        except Exception as error:

            self.logger.error(

                f"Execution Worker Failed | "

                f"{error}"
            )

            raise


    # ====================================
    # RECOVER RUNTIME STATE
    # ====================================

    def recover_runtime_state(self):

        try:

            self.logger.info(
                "Recovering Runtime State"
            )

            positions = (

                self.position_repository
                .load_positions()
            )

            active_orders = (

                self.order_repository
                .load_active_orders()
            )

            self.logger.info(

                f"Recovered Positions | "

                f"{len(positions)}"
            )

            self.logger.info(

                f"Recovered Active Orders | "

                f"{len(active_orders)}"
            )

        except Exception as error:

            self.logger.error(

                f"Recovery Failed | "

                f"{error}"
            )


    # ====================================
    # SHUTDOWN
    # ====================================

    def shutdown(self):

        self.logger.warning(
            "Runtime Shutdown Started"
        )

        try:

            if self.execution_worker:

                self.execution_worker.stop()

            if self.market_generator:

                self.market_generator.stop()

            if self.reconciliation_worker:

                self.reconciliation_worker.stop()

            set_worker_running(False)

        except Exception as error:

            self.logger.error(

                f"Shutdown Failed | "

                f"{error}"
            )

        self.logger.warning(
            "Runtime Shutdown Complete"
        )