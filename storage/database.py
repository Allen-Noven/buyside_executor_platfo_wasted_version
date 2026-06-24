# ====================================
# database.py
# ====================================

import sqlite3


DATABASE_PATH = (
    "storage/trading_system.db"
)


def get_connection():

    connection = sqlite3.connect(

        DATABASE_PATH,

        check_same_thread=False
    )

    return connection