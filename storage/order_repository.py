# ====================================
# order_repository.py
# ====================================

from storage.database import (
    get_connection
)


class OrderRepository:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.connection = (
            get_connection()
        )

        self.create_table()


    # ====================================
    # CREATE TABLE
    # ====================================

    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS orders (

                order_id TEXT PRIMARY KEY,

                symbol TEXT,

                side TEXT,

                quantity REAL,

                filled_quantity REAL,

                strategy TEXT,

                status TEXT,

                created_at TEXT

            )

            """
        )

        self.connection.commit()


    # ====================================
    # SAVE ORDER
    # ====================================

    def save_order(

        self,

        order
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            INSERT OR REPLACE INTO orders (

                order_id,
                symbol,
                side,
                quantity,
                filled_quantity,
                strategy,
                status,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                order.order_id,

                order.symbol,

                order.side,

                order.quantity,

                order.filled_quantity,

                order.strategy,

                order.status,

                str(order.created_at)
            )
        )

        self.connection.commit()


    # ====================================
    # LOAD ACTIVE ORDERS
    # ====================================

    def load_active_orders(self):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            SELECT * FROM orders

            WHERE status != 'COMPLETED'

            """
        )

        return cursor.fetchall()