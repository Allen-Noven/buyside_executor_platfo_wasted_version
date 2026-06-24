# ====================================
# real_time_data_loader.py
# ====================================

import time

from collections import deque

from alpaca.data.historical.stock import (
    StockHistoricalDataClient
)

from alpaca.data.requests import (

    StockLatestTradeRequest,

    StockLatestQuoteRequest
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    DEFAULT_SYMBOL,

    REALTIME_REFRESH_RATE
)

from utils.helpers import (

    format_price,

    format_timestamp
)

from utils.logger import (
    SystemLogger
)


class RealTimeDataLoader:

    def __init__(

        self,

        market_state

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # ALPACA CLIENT
        # ====================================

        self.client = (

            StockHistoricalDataClient(

                API_KEY,

                SECRET_KEY
            )
        )


        # ====================================
        # SHARED MARKET STATE
        # ====================================

        self.market_state = (
            market_state
        )


        # ====================================
        # PRICE HISTORY
        # ====================================

        self.price_window = deque(
            maxlen=20
        )


    # ====================================
    # FETCH MARKET DATA
    # ====================================

    def fetch_latest_data(

        self,

        symbol=DEFAULT_SYMBOL

    ):

        # ====================================
        # LATEST TRADE
        # ====================================

        trade_request = (

            StockLatestTradeRequest(

                symbol_or_symbols=symbol
            )
        )

        latest_trade = (

            self.client.get_stock_latest_trade(

                trade_request
            )
        )

        trade = latest_trade[symbol]


        # ====================================
        # LATEST QUOTE
        # ====================================

        quote_request = (

            StockLatestQuoteRequest(

                symbol_or_symbols=symbol
            )
        )

        latest_quote = (

            self.client.get_stock_latest_quote(

                quote_request
            )
        )

        quote = latest_quote[symbol]


        # ====================================
        # PRICE
        # ====================================

        price = format_price(
            trade.price
        )


        # ====================================
        # STORE PRICE HISTORY
        # ====================================

        self.price_window.append(
            price
        )


        # ====================================
        # SIMPLE VOLATILITY
        # ====================================

        volatility = 0

        if len(self.price_window) > 1:

            returns = []

            prices = list(
                self.price_window
            )

            for i in range(

                1,

                len(prices)
            ):

                ret = (

                    prices[i]
                    - prices[i - 1]

                ) / prices[i - 1]

                returns.append(ret)

            volatility = (

                sum(

                    abs(r)

                    for r in returns
                )

                / len(returns)
            )


        # ====================================
        # LIQUIDITY SCORE
        # ====================================

        spread = (

            quote.ask_price
            - quote.bid_price
        )

        liquidity_score = max(

            0,

            1 - (spread / price)
        )


        return {

            "price":
            price,

            "timestamp":
            format_timestamp(
                trade.timestamp
            ),

            "bid_price":
            format_price(
                quote.bid_price
            ),

            "ask_price":
            format_price(
                quote.ask_price
            ),

            "spread":
            format_price(spread),

            "volatility":
            round(
                volatility,
                4
            ),

            "liquidity_score":
            round(
                liquidity_score,
                4
            )
        }


    # ====================================
    # UPDATE MARKET STATE
    # ====================================

    def update_market_state(

        self,

        market_data

    ):

        self.market_state.update(

            price=
            market_data["price"],

            volume=0,

            timestamp=
            market_data["timestamp"],

            bid_price=
            market_data["bid_price"],

            ask_price=
            market_data["ask_price"],

            volatility=
            market_data["volatility"],

            liquidity_score=
            market_data["liquidity_score"]
        )


    # ====================================
    # START LIVE FEED
    # ====================================

    def run(

        self,

        symbol=DEFAULT_SYMBOL

    ):

        self.logger.info(

            "Starting Real-Time Market Feed"
        )

        while True:

            try:

                # ====================================
                # FETCH MARKET DATA
                # ====================================

                market_data = (

                    self.fetch_latest_data(
                        symbol
                    )
                )


                # ====================================
                # UPDATE MARKET STATE
                # ====================================

                self.update_market_state(
                    market_data
                )


                # ====================================
                # LOG SNAPSHOT
                # ====================================

                self.logger.info(

                    f"Live Market Update | "

                    f"Price: "
                    f"{market_data['price']} | "

                    f"Spread: "
                    f"{market_data['spread']} | "

                    f"Volatility: "
                    f"{market_data['volatility']}"
                )


                # ====================================
                # REFRESH INTERVAL
                # ====================================

                time.sleep(
                    REALTIME_REFRESH_RATE
                )

            except Exception as e:

                self.logger.error(

                    f"Market Feed Error | "
                    f"{e}"
                )

                time.sleep(5)