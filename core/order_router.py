# ====================================
# order_router.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)

from utils.constants import (

    BUY,

    SELL
)


class OrderRouter:

    def __init__(

        self,

        market_state=None,

        oms=None,

        risk_manager=None,

        system_state=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # SHARED COMPONENTS
        # ====================================

        self.market_state = (
            market_state
        )

        self.oms = oms

        self.risk_manager = (
            risk_manager
        )

        self.system_state = (
            system_state
        )

        # ====================================
        # ROUTING STATS
        # ====================================

        self.total_orders_routed = 0

        self.total_rejected_orders = 0

        self.total_filled_orders = 0


    # ====================================
    # ROUTE ORDER
    # ====================================

    def route_order(

        self,

        parent_order,

        child_qty

    ):

        # ====================================
        # VALIDATE INPUT
        # ====================================

        if child_qty <= 0:

            self.logger.error(

                "Invalid Child Quantity"
            )

            return None

        # ====================================
        # RISK CHECK
        # ====================================

        if self.risk_manager:

            approved = (

                self.risk_manager
                .validate_order(

                    symbol=
                    parent_order.symbol,

                    qty=
                    child_qty,

                    side=
                    parent_order.side
                )
            )

            if not approved:

                self.total_rejected_orders += 1

                self.logger.warning(

                    "Order Rejected By Risk"
                )

                return None

        # ====================================
        # MARKET SNAPSHOT
        # ====================================

        market_price = (
            self.market_state
            .current_price
        )

        spread = (
            self.market_state
            .spread
        )

        liquidity = (
            self.market_state
            .liquidity_score
        )

        # ====================================
        # DETERMINE EXECUTION PRICE
        # ====================================

        execution_price = (
            self.determine_execution_price(
                side=parent_order.side
            )
        )

        # ====================================
        # BUILD CHILD ORDER
        # ====================================

        child_order = {

            "timestamp":
            get_current_time(),

            "parent_order_id":
            parent_order.order_id,

            "symbol":
            parent_order.symbol,

            "side":
            parent_order.side,

            "quantity":
            child_qty,

            "execution_price":
            execution_price,

            "market_price":
            market_price,

            "spread":
            spread,

            "liquidity":
            liquidity,

            "strategy":
            parent_order.strategy,

            "status":
            "ROUTED"
        }

        # ====================================
        # SEND TO OMS
        # ====================================

        if self.oms:

            self.oms.submit_market_order(
                
symbol=
        child_order["symbol"],

        qty=
        child_order["quantity"],

        side=
        child_order["side"]

            )

        # ====================================
        # UPDATE PARENT ORDER
        # ====================================

        parent_order.add_child_order(
            child_order
        )

        # ====================================
        # UPDATE STATS
        # ====================================

        self.total_orders_routed += 1

        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"Order Routed | "

            f"{parent_order.symbol} | "

            f"Qty: {child_qty} | "

            f"Price: {execution_price}"
        )

        return child_order


    # ====================================
    # DETERMINE EXECUTION PRICE
    # ====================================

    def determine_execution_price(

        self,

        side

    ):

        bid = (
            self.market_state.bid_price
        )

        ask = (
            self.market_state.ask_price
        )

        mid = (
            self.market_state.mid_price
        )

        spread = (
            self.market_state.spread
        )

        # ====================================
        # FALLBACK
        # ====================================

        if mid == 0:

            return (

                self.market_state
                .current_price
            )

        # ====================================
        # BUY LOGIC
        # ====================================

        if side == BUY:

            # Tight Spread
            if spread <= 0.02:

                return ask

            # Wide Spread
            return round(

                mid + (
                    spread * 0.25
                ),

                2
            )

        # ====================================
        # SELL LOGIC
        # ====================================

        if side == SELL:

            # Tight Spread
            if spread <= 0.02:

                return bid

            # Wide Spread
            return round(

                mid - (
                    spread * 0.25
                ),

                2
            )

        return mid


    # ====================================
    # FILL ORDER
    # ====================================

    def fill_order(

        self,

        parent_order,

        child_order

    ):

        fill_qty = (
            child_order["quantity"]
        )

        fill_price = (
            child_order[
                "execution_price"
            ]
        )

        # ====================================
        # UPDATE PARENT ORDER
        # ====================================

        parent_order.add_fill(

            fill_qty=
            fill_qty,

            fill_price=
            fill_price
        )

        # ====================================
        # UPDATE OMS
        # ====================================

        if self.oms:

            self.oms.record_fill(

                symbol=
                parent_order.symbol,

                qty=
                fill_qty,

                price=
                fill_price
            )

        # ====================================
        # UPDATE STATS
        # ====================================

        self.total_filled_orders += 1

        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"Order Filled | "

            f"{parent_order.symbol} | "

            f"{fill_qty} @ "

            f"{fill_price}"
        )


    # ====================================
    # GET ROUTING STATS
    # ====================================

    def get_stats(self):

        return {

            "total_orders_routed":
            self.total_orders_routed,

            "total_rejected_orders":
            self.total_rejected_orders,

            "total_filled_orders":
            self.total_filled_orders
        }


    # ====================================
    # DISPLAY STATS
    # ====================================

    def show_stats(self):

        stats = (
            self.get_stats()
        )

        print(

            "\n========== ORDER ROUTER ==========\n"
        )

        for key, value in stats.items():

            print(f"{key}: {value}")

        print(

            "\n==================================\n"
        )
