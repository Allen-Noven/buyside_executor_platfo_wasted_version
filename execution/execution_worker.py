# ====================================
# execution_worker.py
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

from utils.config import (
    EXECUTION_INTERVAL
)


class ExecutionWorker:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        order_queue,

        execution_service,

        poll_interval=1
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

        self.order_queue = (
            order_queue
        )

        self.execution_service = (
            execution_service
        )

        # ====================================
        # WORKER CONFIG
        # ====================================

        self.poll_interval = (
            poll_interval
        )

        # ====================================
        # WORKER STATUS
        # ====================================

        self.status = HALTED

        self.processed_orders = 0

        self.failed_orders = 0

        self.current_order = None

        self.logger.info(
            "Execution Worker Initialized"
        )


    # ====================================
    # START WORKER
    # ====================================

    def start(self):

        # ====================================
        # UPDATE STATUS
        # ====================================

        self.status = RUNNING

        self.logger.info(
            "Execution Worker Started"
        )

        print(

            "\n========== EXECUTION WORKER ==========\n"
        )

        # ====================================
        # MAIN LOOP
        # ====================================

        while self.status == RUNNING:

            # ====================================
            # EMPTY QUEUE
            # ====================================

            if self.order_queue.is_empty():

                self.logger.info(
                    "Queue Empty | Waiting..."
                )

                time.sleep(
                    self.poll_interval
                )

                continue

            # ====================================
            # GET NEXT ORDER
            # ====================================

            parent_order = (

                self.order_queue
                .get_next_order()
            )

            if parent_order is None:

                continue

            # ====================================
            # SET CURRENT ORDER
            # ====================================

            self.current_order = (
                parent_order
            )

            self.logger.info(

                f"Processing Order | "

                f"{parent_order.order_id}"
            )

            try:

                # ====================================
                # START ORDER
                # ====================================

                parent_order.start_order()

                # ====================================
                # EXECUTE ORDER
                # ====================================

                result = (

                    self.execution_service
                    .submit_order(
                        parent_order
                    )
                )

                # ====================================
                # SUCCESS
                # ====================================

                if (

                    result["status"]
                    ==
                    COMPLETED
                ):

                    self.processed_orders += 1

                    self.logger.info(

                        f"Order Completed | "

                        f"{parent_order.order_id}"
                    )

                # ====================================
                # FAILURE
                # ====================================

                else:

                    self.failed_orders += 1

                    self.logger.warning(

                        f"Order Failed | "

                        f"{parent_order.order_id}"
                    )

            except Exception as error:

                self.failed_orders += 1

                parent_order.fail_order(
                    str(error)
                )

                self.logger.error(

                    f"Worker Error | "

                    f"{error}"
                )

            finally:

                # ====================================
                # CLEAR CURRENT ORDER
                # ====================================

                self.current_order = None

            # ====================================
            # POLL INTERVAL
            # ====================================

            time.sleep(
                self.poll_interval
            )

        self.logger.warning(
            "Execution Worker Stopped"
        )


    # ====================================
    # STOP WORKER
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(
            "Execution Worker Halted"
        )


    # ====================================
    # GET STATUS
    # ====================================

    def get_status(self):

        return {

            "status":
            self.status,

            "queue_size":
            self.order_queue.size(),

            "processed_orders":
            self.processed_orders,

            "failed_orders":
            self.failed_orders,

            "current_order":
            (

                self.current_order.order_id

                if self.current_order
                else None
            )
        }


    # ====================================
    # IS RUNNING
    # ====================================

    def is_running(self):

        return self.status == RUNNING


    # ====================================
    # SHOW STATUS
    # ====================================

    def show_status(self):

        status = (
            self.get_status()
        )

        print(

            "\n========== EXECUTION WORKER ==========\n"
        )

        for key, value in status.items():

            print(f"{key}: {value}")

        print(

            "\n======================================\n"
        )