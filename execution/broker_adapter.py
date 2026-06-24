# ====================================
# broker_adapter.py
# ====================================

from abc import (
    ABC,
    abstractmethod
)

from alpaca.trading.client import (
    TradingClient
)

from alpaca.trading.requests import (
    MarketOrderRequest
)

from alpaca.trading.enums import (

    OrderSide,

    TimeInForce
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    PAPER_TRADING
)

from utils.constants import (

    BUY,

    SELL
)

from utils.logger import (
    SystemLogger
)


# ====================================
# BASE BROKER ADAPTER
# ====================================

class BrokerAdapter(ABC):


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    @abstractmethod
    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        pass


    # ====================================
    # CANCEL ORDER
    # ====================================

    @abstractmethod
    def cancel_order(

        self,

        order_id
    ):

        pass


    # ====================================
    # GET ORDER
    # ====================================

    @abstractmethod
    def get_order(

        self,

        order_id
    ):

        pass


    # ====================================
    # GET ACCOUNT
    # ====================================

    @abstractmethod
    def get_account(self):

        pass
    # ====================================
    # GET POSITIONS
    # ====================================

    @abstractmethod
    def get_positions(self):

        pass


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    @abstractmethod
    def get_open_orders(self):

        pass


# ====================================
# ALPACA BROKER ADAPTER
# ====================================

class AlpacaBrokerAdapter(BrokerAdapter):


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        super().__init__()

        # ====================================
        # TRADING CLIENT
        # ====================================

        self.client = (

            TradingClient(

                API_KEY,

                SECRET_KEY,

                paper=PAPER_TRADING
            )
        )

        self.logger.info(
            "Alpaca Broker Adapter Initialized"
        )


    # ====================================
    # CONVERT SIDE
    # ====================================

    def convert_side(

        self,

        side
    ):

        if side == BUY:

            return OrderSide.BUY

        elif side == SELL:

            return OrderSide.SELL

        raise ValueError(

            f"Invalid Side | {side}"
        )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        try:

            alpaca_side = (
                self.convert_side(side)
            )

            order_request = (

                MarketOrderRequest(

                    symbol=symbol,

                    qty=qty,

                    side=alpaca_side,

                    time_in_force=
                    TimeInForce.DAY
                )
            )

            order = (

                self.client.submit_order(

                    order_data=
                    order_request
                )
            )

            self.logger.info(

                f"Broker Order Submitted | "

                f"{symbol} | "

                f"{qty}"
            )

            return order

        except Exception as error:

            self.logger.error(

                f"Broker Submit Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # CANCEL ORDER
    # ====================================

    def cancel_order(

        self,

        order_id
    ):

        try:

            self.client.cancel_order_by_id(
                order_id
            )

            self.logger.warning(

                f"Broker Order Cancelled | "

                f"{order_id}"
            )

            return True

        except Exception as error:

            self.logger.error(

                f"Broker Cancel Failed | "

                f"{error}"
            )

            return False


    # ====================================
    # GET ORDER
    # ====================================

    def get_order(

        self,

        order_id
    ):

        try:

            return (

                self.client
                .get_order_by_id(order_id)
            )

        except Exception as error:

            self.logger.error(

                f"Broker Get Order Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # GET ACCOUNT
    # ====================================

    def get_account(self):

        try:

            return (
                self.client.get_account()
            )

        except Exception as error:

            self.logger.error(

                f"Broker Account Failed | "

                f"{error}"
            )

            return None
# ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        try:

            positions = (
                self.client.get_all_positions()
            )

            result = {}

            for position in positions:

                result[position.symbol] = {

                    "quantity":
                    float(position.qty)
                }

            return result

        except Exception as error:

            self.logger.error(

                f"Broker Positions Failed | "

                f"{error}"
            )

            return {}


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    def get_open_orders(self):

        try:

            return (
                self.client.get_orders()
            )

        except Exception as error:

            self.logger.error(

                f"Broker Open Orders Failed | "

                f"{error}"
            )

            return []


# ====================================
# FAKE BROKER ADAPTER
# ====================================

class FakeBrokerAdapter(BrokerAdapter):


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        super().__init__()

        self.orders = {}

        self.logger.info(
            "Fake Broker Adapter Initialized"
        )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        fake_order = {

            "id":
            f"fake_{len(self.orders)+1}",

            "symbol":
            symbol,

            "qty":
            qty,

            "side":
            side,

            "status":
            "filled",

            "filled_avg_price":
            100.0
        }

        self.orders[
            fake_order["id"]
        ] = fake_order

        self.logger.info(

            f"Fake Order Filled | "

            f"{symbol} | "

            f"{qty}"
        )

        return type(

            "FakeOrder",

            (object,),

            fake_order
        )


    # ====================================
    # CANCEL ORDER
    # ====================================

    def cancel_order(

        self,

        order_id
    ):

        if order_id in self.orders:

            self.orders[order_id][
                "status"
            ] = "cancelled"

            self.logger.warning(

                f"Fake Order Cancelled | "

                f"{order_id}"
            )

            return True

        return False


    # ====================================
    # GET ORDER
    # ====================================

    def get_order(

        self,

        order_id
    ):

        return self.orders.get(
            order_id
        )


    # ====================================
    # GET ACCOUNT
    # ====================================

    def get_account(self):

        return {

            "equity":
            100000,

            "cash":
            100000,

            "buying_power":
            400000
        }
    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        return {}


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    def get_open_orders(self):

        return []