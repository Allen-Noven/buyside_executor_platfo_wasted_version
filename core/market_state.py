# ====================================
# market_state.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    format_price,

    format_timestamp
)


class MarketState:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # SYMBOL
        # ====================================

        self.symbol = None

        # ====================================
        # MARKET PRICES
        # ====================================

        self.current_price = 0.0

        self.bid_price = 0.0

        self.ask_price = 0.0

        self.mid_price = 0.0

        self.spread = 0.0

        # ====================================
        # VOLUME
        # ====================================

        self.current_volume = 0

        self.cumulative_volume = 0

        # ====================================
        # VOLATILITY
        # ====================================

        self.volatility = 0.0

        # ====================================
        # LIQUIDITY
        # ====================================

        self.liquidity_score = 100

        # ====================================
        # MICROSTRUCTURE
        # ====================================

        self.order_imbalance = 0.0

        self.trade_intensity = 0.0

        # ====================================
        # MARKET STATUS
        # ====================================

        self.market_open = True

        # ====================================
        # TIMESTAMP
        # ====================================

        self.timestamp = None


    # ====================================
    # UPDATE MARKET STATE
    # ====================================

    def update(

        self,

        symbol=None,

        price=None,

        volume=None,

        bid_price=None,

        ask_price=None,

        volatility=None,

        liquidity_score=None,

        order_imbalance=None,

        trade_intensity=None,

        timestamp=None

    ):

        # ====================================
        # SYMBOL
        # ====================================

        if symbol is not None:

            self.symbol = symbol

        # ====================================
        # CURRENT PRICE
        # ====================================

        if price is not None:

            self.current_price = (
                format_price(price)
            )

        # ====================================
        # BID PRICE
        # ====================================

        if bid_price is not None:

            self.bid_price = (
                format_price(bid_price)
            )

        # ====================================
        # ASK PRICE
        # ====================================

        if ask_price is not None:

            self.ask_price = (
                format_price(ask_price)
            )

        # ====================================
        # MID PRICE
        # ====================================

        if (

            self.bid_price > 0
            and
            self.ask_price > 0

        ):

            self.mid_price = round(

                (

                    self.bid_price
                    +
                    self.ask_price

                ) / 2,

                2
            )

            self.spread = round(

                self.ask_price
                -
                self.bid_price,

                4
            )

        # ====================================
        # VOLUME
        # ====================================

        if volume is not None:

            self.current_volume = (
                int(volume)
            )

            self.cumulative_volume += (
                int(volume)
            )

        # ====================================
        # VOLATILITY
        # ====================================

        if volatility is not None:

            self.volatility = round(

                float(volatility),

                4
            )

        # ====================================
        # LIQUIDITY
        # ====================================

        if liquidity_score is not None:

            self.liquidity_score = round(

                float(liquidity_score),

                2
            )

        # ====================================
        # ORDER IMBALANCE
        # ====================================

        if order_imbalance is not None:

            self.order_imbalance = round(

                float(order_imbalance),

                4
            )

        # ====================================
        # TRADE INTENSITY
        # ====================================

        if trade_intensity is not None:

            self.trade_intensity = round(

                float(trade_intensity),

                4
            )

        # ====================================
        # TIMESTAMP
        # ====================================

        if timestamp is not None:

            self.timestamp = timestamp

        # ====================================
        # LOG UPDATE
        # ====================================

        self.logger.info(

            f"Market Update | "

            f"Symbol: {self.symbol} | "

            f"Price: {self.current_price} | "

            f"Spread: {self.spread} | "

            f"Volume: {self.current_volume}"
        )


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_snapshot(self):

        return {

            "symbol":
            self.symbol,

            "current_price":
            self.current_price,

            "bid_price":
            self.bid_price,

            "ask_price":
            self.ask_price,

            "mid_price":
            self.mid_price,

            "spread":
            self.spread,

            "current_volume":
            self.current_volume,

            "cumulative_volume":
            self.cumulative_volume,

            "volatility":
            self.volatility,

            "liquidity_score":
            self.liquidity_score,

            "order_imbalance":
            self.order_imbalance,

            "trade_intensity":
            self.trade_intensity,

            "market_open":
            self.market_open,

            "timestamp":
            format_timestamp(
                self.timestamp
            )
        }


    # ====================================
    # DISPLAY STATE
    # ====================================

    def show(self):

        snapshot = (
            self.get_snapshot()
        )

        print(

            "\n========== MARKET STATE ==========\n"
        )

        for key, value in snapshot.items():

            print(f"{key}: {value}")

        print(

            "\n==================================\n"
        )


    # ====================================
    # RESET MARKET STATE
    # ====================================

    def reset(self):

        self.__init__()

        self.logger.warning(
            "Market State Reset"
        )