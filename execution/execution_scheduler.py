# ====================================
# execution_scheduler.py
# ====================================

import time

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    RUNNING,

    HALTED,

    COMPLETED
)


class ExecutionScheduler:

    def __init__(

        self,

        execution_interval=1,

        market_state=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # EXECUTION TIMING
        # ====================================

        self.execution_interval = (
            execution_interval
        )


        # ====================================
        # MARKET STATE
        # ====================================

        self.market_state = (
            market_state
        )


        # ====================================
        # EXECUTION STATE
        # ====================================

        self.status = RUNNING

        self.current_slice = 0

        self.total_slices = 0


    # ====================================
    # DYNAMIC EXECUTION INTERVAL
    # ====================================

    def get_dynamic_interval(self):

        if self.market_state is None:

            return self.execution_interval


        volatility = (
            self.market_state.volatility
        )


        if volatility is None:

            return self.execution_interval


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if volatility > 0.05:

            return (

                self.execution_interval * 2
            )


        # ====================================
        # LOW VOLATILITY
        # ====================================

        elif volatility < 0.01:

            return (

                self.execution_interval * 0.5
            )


        return self.execution_interval


    # ====================================
    # RUN EXECUTION SCHEDULE
    # ====================================

    def run_schedule(

        self,

        schedule,

        execution_callback

    ):

        self.total_slices = (
            len(schedule)
        )


        self.logger.info(

            f"Starting Execution Schedule | "

            f"{self.total_slices} slices"
        )


        # ====================================
        # EXECUTION LOOP
        # ====================================

        for child_order in schedule:

            # ====================================
            # HALTED
            # ====================================

            if self.status == HALTED:

                self.logger.warning(

                    "Execution Halted"
                )

                break


            self.current_slice += 1


            self.logger.info(

                f"Executing Slice "

                f"{self.current_slice}/"

                f"{self.total_slices}"
            )


            self.logger.info(

                f"Qty: "
                f"{child_order['qty']}"
            )


            # ====================================
            # EXECUTE CHILD ORDER
            # ====================================

            execution_callback(
                child_order
            )


            # ====================================
            # DYNAMIC EXECUTION TIMING
            # ====================================

            interval = (
                self.get_dynamic_interval()
            )


            self.logger.info(

                f"Waiting "
                f"{interval} seconds"
            )


            time.sleep(interval)


        self.status = COMPLETED


        self.logger.info(
            "Execution Schedule Completed"
        )


    # ====================================
    # STOP EXECUTION
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(

            "Scheduler Stopped"
        )


    # ====================================
    # RESUME EXECUTION
    # ====================================

    def resume(self):

        self.status = RUNNING

        self.logger.info(

            "Scheduler Resumed"
        )


    # ====================================
    # GET STATUS
    # ====================================

    def get_status(self):

        return {

            "status":
            self.status,

            "current_slice":
            self.current_slice,

            "total_slices":
            self.total_slices
        }


    # ====================================
    # SHOW SCHEDULE
    # ====================================

    def show_schedule(

        self,

        schedule

    ):

        print(

            "\n========== EXECUTION SCHEDULE ==========\n"
        )

        for child_order in schedule:

            print(child_order)

        print(

            "\n========================================\n"
        )