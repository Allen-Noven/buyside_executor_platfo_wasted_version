# ====================================
# base_oms.py
# ====================================

class BaseOMS:


    # ====================================
    # SUBMIT MARKET ORDER
    # ====================================

    def submit_market_order(

        self,

        symbol,

        qty,

        side
    ):

        raise NotImplementedError