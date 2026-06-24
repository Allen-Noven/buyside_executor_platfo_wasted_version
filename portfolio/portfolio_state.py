# ====================================
# portfolio_state.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    format_price
)


class PortfolioState:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        position_manager
    ):

        self.logger = (
            SystemLogger()
        )

        self.position_manager = (
            position_manager
        )


    # ====================================
    # GET TOTAL POSITIONS
    # ====================================

    def get_total_positions(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        return len(positions)


    # ====================================
    # GET GROSS EXPOSURE
    # ====================================

    def get_gross_exposure(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        gross_exposure = 0

        for symbol in positions:

            gross_exposure += abs(

                positions[symbol][
                    "market_value"
                ]
            )

        return format_price(
            gross_exposure
        )


    # ====================================
    # GET NET EXPOSURE
    # ====================================

    def get_net_exposure(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        net_exposure = 0

        for symbol in positions:

            net_exposure += (

                positions[symbol][
                    "market_value"
                ]
            )

        return format_price(
            net_exposure
        )


    # ====================================
    # GET LONG EXPOSURE
    # ====================================

    def get_long_exposure(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        long_exposure = 0

        for symbol in positions:

            market_value = (

                positions[symbol][
                    "market_value"
                ]
            )

            if market_value > 0:

                long_exposure += (
                    market_value
                )

        return format_price(
            long_exposure
        )


    # ====================================
    # GET SHORT EXPOSURE
    # ====================================

    def get_short_exposure(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        short_exposure = 0

        for symbol in positions:

            market_value = (

                positions[symbol][
                    "market_value"
                ]
            )

            if market_value < 0:

                short_exposure += abs(
                    market_value
                )

        return format_price(
            short_exposure
        )


    # ====================================
    # GET TOTAL MARKET VALUE
    # ====================================

    def get_total_market_value(self):

        return self.get_net_exposure()


    # ====================================
    # GET PORTFOLIO SUMMARY
    # ====================================

    def get_portfolio_summary(self):

        return {

            "total_positions":

            self.get_total_positions(),

            "gross_exposure":

            self.get_gross_exposure(),

            "net_exposure":

            self.get_net_exposure(),

            "long_exposure":

            self.get_long_exposure(),

            "short_exposure":

            self.get_short_exposure(),

            "total_market_value":

            self.get_total_market_value()
        }


    # ====================================
    # SHOW PORTFOLIO SUMMARY
    # ====================================

    def show_portfolio_summary(self):

        summary = (
            self.get_portfolio_summary()
        )

        print(

            "\n========== "
            "PORTFOLIO SUMMARY "
            "==========\n"
        )

        print(

            f"Total Positions: "

            f"{summary['total_positions']}"
        )

        print(

            f"Gross Exposure: "

            f"{summary['gross_exposure']}"
        )

        print(

            f"Net Exposure: "

            f"{summary['net_exposure']}"
        )

        print(

            f"Long Exposure: "

            f"{summary['long_exposure']}"
        )

        print(

            f"Short Exposure: "

            f"{summary['short_exposure']}"
        )

        print(

            f"Total Market Value: "

            f"{summary['total_market_value']}"
        )

        print(

            "\n==============================="
            "===================\n"
        )

        self.logger.info(

            "Portfolio summary updated"
        )