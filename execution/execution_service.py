# ====================================
# execution_service.py
# ====================================

from storage.order_repository import (
    OrderRepository
)

from storage.fill_repository import (
    FillRepository
)

from storage.position_repository import (
    PositionRepository
)

from storage.execution_repository import (
    ExecutionRepository
)

from execution.execution_scheduler import (
    ExecutionScheduler
)

from execution.fill_tracker import (
    FillTracker
)

from execution.execution_log import (
    ExecutionAuditLogger
)

from analytics.slippage_analyzer import (
    SlippageAnalyzer
)

from analytics.pnl_tracker import (
    PnLTracker
)

from data.market_event_bus import (
    MarketEventBus
)

from risk.risk_manager import (
    RiskManager
)

from risk.liquidity_monitor import (
    LiquidityMonitor
)

from core.market_state import (
    MarketState
)

from core.redis_state import (
    RedisState
)

from portfolio.position_manager import (
    PositionManager
)

from strategies.twap import (
    TWAPStrategy
)

from strategies.adaptive_vwap import (
    AdaptiveVWAPStrategy
)

from strategies.pov import (
    POVStrategy
)

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    TWAP,

    VWAP,

    POV,

    RUNNING,

    HALTED,

    COMPLETED,

    ORDER_FILLED_EVENT,

    EXECUTION_STARTED,

    EXECUTION_COMPLETED,

    MARKET_UPDATE_EVENT
)

from utils.config import (

    EXECUTION_INTERVAL,

    DEFAULT_PARTICIPATION
)


class ExecutionService:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state=None,

        event_bus=None,

        oms=None,

        position_manager=None
    ):

        # ====================================
        # LOGGERS
        # ====================================

        self.logger = (
            SystemLogger()
        )

        self.execution_file_logger = (
            SystemLogger(
                log_type="execution"
            )
        )

        # ====================================
        # STORAGE
        # ====================================

        self.order_repository = (
            OrderRepository()
        )

        self.fill_repository = (
            FillRepository()
        )

        self.position_repository = (
            PositionRepository()
        )

        self.execution_repository = (
            ExecutionRepository()
        )

        # ====================================
        # REDIS
        # ====================================

        self.redis_state = (
            RedisState()
        )

        # ====================================
        # MARKET STATE
        # ====================================

        self.market_state = (

            market_state
            if market_state
            else MarketState()
        )

        # ====================================
        # EVENT BUS
        # ====================================

        self.event_bus = (

            event_bus
            if event_bus
            else MarketEventBus()
        )

        # ====================================
        # OMS
        # ====================================

        if oms is None:

            raise RuntimeError(
                "OMS dependency required"
            )

        self.oms = oms

        # ====================================
        # POSITION MANAGER
        # ====================================

        self.position_manager = (

            position_manager
            if position_manager
            else PositionManager()
        )

        # ====================================
        # EXECUTION AUDIT LOGGER
        # ====================================

        self.execution_logger = (
            ExecutionAuditLogger()
        )

        # ====================================
        # FILL TRACKER
        # ====================================

        self.fill_tracker = (
            FillTracker()
        )

        # ====================================
        # ANALYTICS
        # ====================================

        self.slippage_analyzer = (
            SlippageAnalyzer()
        )

        self.pnl_tracker = (
            PnLTracker()
        )

        # ====================================
        # RISK MANAGER
        # ====================================

        self.risk_manager = (

            RiskManager(

                market_state=
                self.market_state
            )
        )

        # ====================================
        # LIQUIDITY MONITOR
        # ====================================

        self.liquidity_monitor = (

            LiquidityMonitor(

                market_state=
                self.market_state
            )
        )

        # ====================================
        # ACTIVE ORDERS
        # ====================================

        self.active_orders = {}

        # ====================================
        # STATUS
        # ====================================

        self.status = RUNNING

        # ====================================
        # MARKET EVENT SUBSCRIPTION
        # ====================================

        self.event_bus.subscribe(

            MARKET_UPDATE_EVENT,

            self.on_market_update
        )

        self.logger.info(
            "Execution Service Initialized"
        )


    # ====================================
    # MARKET UPDATE
    # ====================================

    def on_market_update(

        self,

        market_event
    ):

        try:

            self.logger.info(

                f"Market Update | "

                f"{market_event['symbol']} | "

                f"{market_event['price']}"
            )

        except Exception as error:

            self.logger.error(

                f"Market Update Failed | "

                f"{error}"
            )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        parent_order
    ):

        try:

            parent_order.start_order()

            self.order_repository.save_order(
                parent_order
            )

            self.active_orders[
                parent_order.order_id
            ] = parent_order

            self.execution_file_logger.info(

                f"Execution Started | "

                f"OrderID={parent_order.order_id} | "

                f"{parent_order.symbol} | "

                f"{parent_order.strategy} | "

                f"Qty={parent_order.quantity} | "

                f"Side={parent_order.side}"
            )

            self.event_bus.publish(

                EXECUTION_STARTED,

                parent_order.get_snapshot()
            )

            strategy = (
                self.create_strategy(
                    parent_order
                )
            )

            if hasattr(

                strategy,

                "generate_schedule"
            ):

                schedule = (
                    strategy.generate_schedule()
                )

            else:

                schedule = []

                while (

                    strategy.remaining_qty > 0
                ):

                    next_order = (
                        strategy.get_next_order()
                    )

                    if next_order is None:

                        break

                    schedule.append(
                        next_order
                    )

            scheduler = (

                ExecutionScheduler(

                    execution_interval=
                    EXECUTION_INTERVAL,

                    market_state=
                    self.market_state
                )
            )

            scheduler.run_schedule(

                schedule,

                lambda child_order:
                self.execute_child_order(

                    parent_order,

                    child_order
                )
            )

            parent_order.complete_order()

            self.order_repository.save_order(
                parent_order
            )

            self.execution_repository.save_execution(

                parent_order.get_snapshot()
            )

            self.event_bus.publish(

                EXECUTION_COMPLETED,

                parent_order.get_snapshot()
            )

            self.active_orders.pop(

                parent_order.order_id,

                None
            )

            self.execution_file_logger.info(

                f"Execution Completed | "

                f"OrderID={parent_order.order_id} | "

                f"{parent_order.symbol}"
            )

            return {

                "status":
                COMPLETED,

                "order_id":
                parent_order.order_id
            }

        except Exception as error:

            parent_order.halt_order(
                str(error)
            )

            self.logger.error(

                f"Execution Failed | "

                f"{error}"
            )

            return {

                "status":
                HALTED,

                "reason":
                str(error)
            }


    # ====================================
    # EXECUTE CHILD ORDER
    # ====================================

    def execute_child_order(

        self,

        parent_order,

        child_order
    ):

        qty = child_order["qty"]

        liquidity_result = (

            self.liquidity_monitor
            .evaluate_market()
        )

        if (

            liquidity_result[
                "market_quality"
            ] == "POOR"

        ):

            self.logger.warning(
                "Liquidity Check Failed"
            )

            return

        risk_ok = (

            self.risk_manager
            .validate_order(

                qty=qty,

                current_position=
                parent_order.filled_quantity
            )
        )

        if not risk_ok:

            self.logger.warning(
                "Risk Check Failed"
            )

            return

        arrival_price = (
            self.market_state.current_price
        )

        order = (

            self.oms.submit_market_order(

                symbol=
                parent_order.symbol,

                qty=
                qty,

                side=
                parent_order.side
            )
        )

        if order is None:

            self.logger.error(
                "OMS Submission Failed"
            )

            return

        if order.filled_avg_price:

            fill_price = float(
                order.filled_avg_price
            )

        else:

            fill_price = arrival_price

        parent_order.add_fill(

            fill_qty=
            qty,

            fill_price=
            fill_price
        )

        self.fill_tracker.record_fill(

            order_id=
            str(order.id),

            symbol=
            parent_order.symbol,

            qty=
            qty,

            fill_price=
            fill_price,

            status=
            str(order.status),

            side=
            parent_order.side,

            strategy=
            parent_order.strategy
        )

        self.position_manager.update_position(

            symbol=
            parent_order.symbol,

            side=
            parent_order.side,

            qty=
            qty,

            fill_price=
            fill_price,

            market_price=
            self.market_state.current_price
        )

        self.event_bus.publish(

            ORDER_FILLED_EVENT,

            {

                "order_id":
                parent_order.order_id,

                "symbol":
                parent_order.symbol,

                "side":
                parent_order.side,

                "qty":
                qty,

                "fill_price":
                fill_price
            }
        )

        self.execution_file_logger.info(

            f"Child Order Executed | "

            f"ParentOrderID={parent_order.order_id} | "

            f"BrokerOrderID={order.id} | "

            f"{parent_order.symbol} | "

            f"Side={parent_order.side} | "

            f"Qty={qty} | "

            f"FillPrice={fill_price}"
        )


    # ====================================
    # CREATE STRATEGY
    # ====================================

    def create_strategy(

        self,

        parent_order
    ):

        if parent_order.strategy == TWAP:

            return TWAPStrategy(

                total_qty=
                parent_order.quantity,

                total_minutes=1,

                slices=5
            )

        elif parent_order.strategy == VWAP:

            return AdaptiveVWAPStrategy(

                total_qty=
                parent_order.quantity,

                target_participation=
                DEFAULT_PARTICIPATION,

                market_state=
                self.market_state
            )

        elif parent_order.strategy == POV:

            return POVStrategy(

                total_qty=
                parent_order.quantity
            )

        raise ValueError(

            f"Unsupported Strategy | "

            f"{parent_order.strategy}"
        )


    # ====================================
    # GET ACTIVE ORDERS
    # ====================================

    def get_active_orders(self):

        return {

            order_id:
            order.get_snapshot()

            for order_id, order

            in self.active_orders.items()
        }


    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        return (

            self.position_manager
            .get_all_positions()
        )


    # ====================================
    # STOP EXECUTION
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(
            "Execution Service Halted"
        )