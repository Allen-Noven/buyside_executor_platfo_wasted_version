# ====================================
# live_feed.py
# ====================================

from data.feeds.base_feed import (
    BaseFeed
)

from data.real_time_data_loader import (
    RealTimeDataLoader
)


class LiveFeed(BaseFeed):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        loader
    ):

        self.loader = (
            loader
        )


    # ====================================
    # START
    # ====================================

    def start(self):

        self.loader.start()


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        pass


    # ====================================
    # SUBSCRIBE
    # ====================================

    def subscribe(

        self,

        symbol
    ):

        pass