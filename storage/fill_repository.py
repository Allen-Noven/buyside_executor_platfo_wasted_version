# ====================================
# fill_repository.py
# ====================================

from storage.database import (
    get_connection
)


class FillRepository:


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

            CREATE TABLE IF NOT EXISTS fills (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                order_id TEXT,

                symbol TEXT,

                side TEXT,

                qty REAL,

                fill_price REAL,

                timestamp TEXT

            )

            """
        )

        self.connection.commit()


    # ====================================
    # SAVE FILL
    # ====================================

    def save_fill(

        self,

        fill
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            INSERT INTO fills (

                order_id,
                symbol,
                side,
                qty,
                fill_price,
                timestamp

            )

            VALUES (?, ?, ?, ?, ?, ?)

            """,

            (

                fill["order_id"],

                fill["symbol"],

                fill["side"],

                fill["qty"],

                fill["fill_price"],

                fill["timestamp"]
            )
        )

        self.connection.commit()