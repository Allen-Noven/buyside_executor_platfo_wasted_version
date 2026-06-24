# ====================================
# order_entry.py
# ====================================

import requests
import streamlit as st


# ====================================
# API CONFIG
# ====================================

API_URL = (
    "http://localhost:8000"
)


class OrderEntryPanel:


    # ====================================
    # RENDER
    # ====================================

    def render(self):

        st.subheader(
            "Order Entry"
        )

        # ====================================
        # SYMBOL
        # ====================================

        symbol = st.text_input(

            "Symbol",

            value="NVDA"
        )

        # ====================================
        # SIDE
        # ====================================

        side = st.selectbox(

            "Side",

            [

                "BUY",

                "SELL"
            ]
        )

        # ====================================
        # QUANTITY
        # ====================================

        qty = st.number_input(

            "Quantity",

            min_value=1,

            value=100
        )

        # ====================================
        # STRATEGY
        # ====================================

        strategy = st.selectbox(

            "Strategy",

            [

                "TWAP",

                "VWAP",

                "POV"
            ]
        )

        # ====================================
        # SUBMIT BUTTON
        # ====================================

        if st.button(

            "Submit Order",

            use_container_width=True
        ):

            self.submit_order(

                symbol=
                symbol,

                qty=
                qty,

                side=
                side,

                strategy=
                strategy
            )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        symbol,

        qty,

        side,

        strategy
    ):

        try:

            payload = {

                "symbol":
                symbol,

                "qty":
                qty,

                "side":
                side,

                "strategy":
                strategy
            }

            response = requests.post(

                f"{API_URL}/order",

                json=payload
            )

            # ====================================
            # SUCCESS
            # ====================================

            if response.status_code == 200:

                result = response.json()

                st.success(

                    f"Order Submitted | "

                    f"{result['order_id']}"
                )

                st.json(result)

            # ====================================
            # FAILURE
            # ====================================

            else:

                st.error(

                    f"Order Failed | "

                    f"{response.text}"
                )

        except Exception as error:

            st.error(

                f"Connection Failed | "

                f"{error}"
            )