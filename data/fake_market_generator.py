# ====================================
# fake_market_generator.py
# ====================================

import time
import random
import threading

from utils.logger import (
    SystemLogger
)

from utils.constants import (
    MARKET_UPDATE_EVENT
)

from utils.config import (
    FAKE_MARKET_INTERVAL
)

from utils.helpers import (
    get_current_time
)


class SimulationMarketGenerator:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state,

        event_bus,

        symbol="NVDA",

        start_price=172.0,

        price_volatility=0.5
    ):

        self.logger = (
            SystemLogger()
        )

        self.market_state = (
            market_state
        )

        self.event_bus = (
            event_bus
        )

        self.symbol = (
            symbol
        )

        self.price = (
            start_price
        )

        self.price_volatility = (
            price_volatility
        )

        self.running = False

        self.market_thread = None

        self.logger.info(

            f"Simulation Market Generator Initialized | "

            f"{self.symbol}"
        )


    # ====================================
    # START ASYNC
    # ====================================

    def start_async(self):

        self.market_thread = threading.Thread(

            target=self.start,

            daemon=True
        )

        self.market_thread.start()

        self.logger.info(
            "Simulation Market Thread Started"
        )


    # ====================================
    # START GENERATOR
    # ====================================

    def start(self):

        self.logger.warning(

            f"Starting Simulation Market | "

            f"{self.symbol}"
        )

        self.running = True

        while self.running:

            try:

                # ====================================
                # RANDOM WALK
                # ====================================

                self.price += random.uniform(

                    -self.price_volatility,

                    self.price_volatility
                )

                self.price = round(
                    self.price,
                    2
                )

                # ====================================
                # SPREAD
                # ====================================

                spread = round(

                    random.uniform(
                        0.01,
                        0.08
                    ),

                    2
                )

                bid_price = round(
                    self.price - spread / 2,
                    2
                )

                ask_price = round(
                    self.price + spread / 2,
                    2
                )

                # ====================================
                # VOLUME
                # ====================================

                volume = random.randint(
                    1000,
                    10000
                )

                # ====================================
                # LIQUIDITY
                # ====================================

                liquidity_score = random.randint(
                    20,
                    100
                )

                # ====================================
                # VOLATILITY
                # ====================================

                simulated_volatility = round(

                    random.uniform(
                        0.1,
                        3.0
                    ),

                    2
                )

                # ====================================
                # UPDATE MARKET STATE
                # ====================================

                self.market_state.update(

                    symbol=
                    self.symbol,

                    price=
                    self.price,

                    volume=
                    volume,

                    bid_price=
                    bid_price,

                    ask_price=
                    ask_price,

                    volatility=
                    simulated_volatility,

                    liquidity_score=
                    liquidity_score
                )

                # ====================================
                # EVENT PAYLOAD
                # ====================================

                market_event = {

                    "timestamp":
                    get_current_time(),

                    "symbol":
                    self.symbol,

                    "price":
                    self.price,

                    "bid_price":
                    bid_price,

                    "ask_price":
                    ask_price,

                    "spread":
                    spread,

                    "volume":
                    volume,

                    "volatility":
                    simulated_volatility,

                    "liquidity_score":
                    liquidity_score
                }

                # ====================================
                # PUBLISH EVENT
                # ====================================

                self.event_bus.publish(

                    MARKET_UPDATE_EVENT,

                    market_event
                )

                # ====================================
                # LOG
                # ====================================

                self.logger.info(

                    f"Simulation Tick | "

                    f"{self.symbol} | "

                    f"Price={self.price}"
                )

                # ====================================
                # WAIT
                # ====================================

                time.sleep(
                    FAKE_MARKET_INTERVAL
                )

            except Exception as error:

                self.logger.error(

                    f"Simulation Market Error | "

                    f"{error}"
                )

                time.sleep(1)


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        self.running = False

        self.logger.warning(
            "Simulation Market Generator Stopped"
        )