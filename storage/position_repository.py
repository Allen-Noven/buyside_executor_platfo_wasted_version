# ====================================
# position_repository.py
# ====================================

from storage.database import (
    get_connection
)


class PositionRepository:


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

            CREATE TABLE IF NOT EXISTS positions (

                symbol TEXT PRIMARY KEY,

                quantity REAL,

                average_price REAL,

                unrealized_pnl REAL,

                realized_pnl REAL

            )

            """
        )

        self.connection.commit()


    # ====================================
    # SAVE POSITION
    # ====================================

    def save_position(

        self,

        position
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            INSERT OR REPLACE INTO positions (

                symbol,
                quantity,
                average_price,
                unrealized_pnl,
                realized_pnl

            )

            VALUES (?, ?, ?, ?, ?)

            """,

            (

                position["symbol"],

                position["quantity"],

                position["average_price"],

                position["unrealized_pnl"],

                position["realized_pnl"]
            )
        )

        self.connection.commit()


    # ====================================
    # LOAD POSITIONS
    # ====================================

    def load_positions(self):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            SELECT * FROM positions

            """
        )

        return cursor.fetchall()


    # ====================================
    # GET POSITION
    # ====================================

    def get_position(

        self,

        symbol
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            SELECT * FROM positions

            WHERE symbol = ?

            """,

            (symbol,)
        )

        return cursor.fetchone()


    # ====================================
    # DELETE POSITION
    # ====================================

    def delete_position(

        self,

        symbol
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            DELETE FROM positions

            WHERE symbol = ?

            """,

            (symbol,)
        )

        self.connection.commit()


    # ====================================
    # CLEAR POSITIONS
    # ====================================

    def clear_positions(self):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            DELETE FROM positions

            """
        )

        self.connection.commit()


    # ====================================
    # CLOSE
    # ====================================

    def close(self):

        self.connection.close()