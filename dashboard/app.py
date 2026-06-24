# ====================================
# app.py
# ====================================

import os
import sys
import json
import time
import threading

import streamlit as st
import websocket

from dashboard.order_entry import (
    OrderEntryPanel
)

from dashboard.pnl_dashboard import (
    PnLDashboard
)

from utils.runtime_mode import (
    RUNTIME_MODE
)

from utils.config import (
    DATA_MODE
)
from utils.runtime_mode import (
    RUNTIME_MODE
)


# ====================================
# ADD PROJECT ROOT
# ====================================

PROJECT_ROOT = os.path.dirname(

    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.append(PROJECT_ROOT)


# ====================================
# PAGE CONFIG
# ====================================

st.set_page_config(

    page_title=
    "Smart Execution Dashboard",

    layout="wide"
)


# ====================================
# WEBSOCKET URL
# ====================================

WEBSOCKET_URL = (
    "ws://localhost:8000/ws"
)


# ====================================
# SESSION STATE INIT
# ====================================

if "initialized" not in st.session_state:

    st.session_state.initialized = True

    st.session_state.websocket_connected = False

    st.session_state.ws_started = False

    st.session_state.market_data = {

        "symbol":
        "NVDA",

        "price":
        0,

        "spread":
        0,

        "liquidity":
        0
    }

    st.session_state.execution_status = {

        "status":
        "IDLE",

        "halted":
        False,

        "reason":
        None
    }

    st.session_state.execution_summary = {

        "strategy":
        "N/A",

        "filled_qty":
        0,

        "remaining_qty":
        0,

        "completion":
        0
    }

    st.session_state.fills = []

    st.session_state.alerts = []


# ====================================
# WEBSOCKET CALLBACKS
# ====================================

def on_open(ws):

    st.session_state.websocket_connected = True

    print(
        "WebSocket Connected"
    )


def on_close(

    ws,

    close_status_code,

    close_msg
):

    st.session_state.websocket_connected = False

    print(
        "WebSocket Disconnected"
    )


def on_error(

    ws,

    error
):

    st.session_state.websocket_connected = False

    print(

        f"WebSocket Error | "

        f"{error}"
    )


def on_message(

    ws,

    message
):

    try:

        data = json.loads(
            message
        )

        event = data.get(
            "event"
        )

        payload = data.get(
            "payload",
            {}
        )

        # ====================================
        # MARKET UPDATE
        # ====================================

        if event == "MARKET_UPDATE":

            st.session_state.market_data.update(
                payload
            )

        # ====================================
        # ORDER UPDATE
        # ====================================

        elif event == "ORDER_UPDATE":

            st.session_state.execution_status = {

                "status":
                payload.get(
                    "status",
                    "UNKNOWN"
                ),

                "halted":
                payload.get(
                    "status"
                ) == "HALTED",

                "reason":
                payload.get(
                    "reason"
                )
            }

        # ====================================
        # FILL UPDATE
        # ====================================

        elif event == "FILL_UPDATE":

            st.session_state.fills.append(
                payload
            )

            total_filled = sum(

                fill.get(
                    "qty",
                    0
                )

                for fill in
                st.session_state.fills
            )

            st.session_state.execution_summary[
                "filled_qty"
            ] = total_filled

        # ====================================
        # POSITION UPDATE
        # ====================================

        elif event == "POSITION_UPDATE":

            portfolio = payload.get(
                "portfolio",
                {}
            )

            st.session_state.execution_summary[
                "portfolio"
            ] = portfolio

        # ====================================
        # EXECUTION COMPLETED
        # ====================================

        elif event == "EXECUTION_COMPLETED":

            st.session_state.execution_status = {

                "status":
                "COMPLETED",

                "halted":
                False,

                "reason":
                None
            }

        # ====================================
        # RISK ALERT
        # ====================================

        elif event == "RISK_ALERT":

            st.session_state.alerts.append(

                payload.get(
                    "message",
                    "Unknown Alert"
                )
            )

    except Exception as error:

        print(

            f"Message Parse Failed | "

            f"{error}"
        )


# ====================================
# WEBSOCKET THREAD
# ====================================

def websocket_listener():

    ws = websocket.WebSocketApp(

        WEBSOCKET_URL,

        on_open=on_open,

        on_close=on_close,

        on_error=on_error,

        on_message=on_message
    )

    ws.run_forever()


# ====================================
# START WEBSOCKET
# ====================================

if not st.session_state.ws_started:

    websocket_thread = threading.Thread(

        target=
        websocket_listener,

        daemon=True
    )

    websocket_thread.start()

    st.session_state.ws_started = True


# ====================================
# TITLE
# ====================================

st.title(
    "Smart Execution Dashboard"

)
# ====================================
# RUNTIME MODE BANNER
# ====================================

if RUNTIME_MODE == "LIVE":

    st.error(
        "🚨 LIVE TRADING MODE"
    )

elif RUNTIME_MODE == "PAPER":

    st.warning(
        "🟡 PAPER TRADING MODE"
    )

else:

    st.success(
        "✅ SIMULATION MODE"
    )
# ====================================
# RUNTIME ALERT STORAGE
# ====================================

if "runtime_alerts" not in st.session_state:

    st.session_state.runtime_alerts = []

# ====================================
# WEBSOCKET MESSAGE
# ====================================

def on_message(

    ws,

    message
):

    try:

        data = json.loads(
            message
        )

        event = data.get(
            "event"
        )

        payload = data.get(
            "payload",
            {}
        )

        # ====================================
        # SYSTEM ERROR
        # ====================================

        if event == "SYSTEM_ERROR":

            error_message = payload.get(
                "message",
                "Unknown Error"
            )

            st.session_state.runtime_alerts.append(

                f"🚨 {error_message}"
            )

    except Exception as error:

        print(

            f"WebSocket Error | "

            f"{error}"
        )
# ====================================
# RUNTIME STATUS
# ====================================
st.sidebar.success(
    f"Runtime Mode: {RUNTIME_MODE}"
)

st.subheader(
    "Runtime Status"
)

col1, col2 = st.columns(2)

with col1:

    st.info(

        f"MODE: "
        f"{RUNTIME_MODE}"
    )

with col2:

    st.info(

        f"DATA MODE: "
        f"{DATA_MODE}"
    )


# ====================================
# CONNECTION STATUS
# ====================================

if st.session_state.websocket_connected:

    st.success(
        "WebSocket Connected"
    )

else:

    st.error(
        "WebSocket Disconnected"
    )


st.markdown("---")


# ====================================
# ORDER ENTRY
# ====================================

st.subheader(
    "Order Entry"
)

order_entry = (
    OrderEntryPanel()
)

order_entry.render()


st.markdown("---")


# ====================================
# MARKET STATE
# ====================================

market_data = (
    st.session_state.market_data
)

st.subheader(
    "Market State"
)

col1, col2, col3 = (
    st.columns(3)
)

with col1:

    st.metric(

        "Price",

        market_data.get(
            "price",
            0
        )
    )

with col2:

    st.metric(

        "Spread",

        market_data.get(
            "spread",
            0
        )
    )

with col3:

    st.metric(

        "Liquidity",

        market_data.get(
            "liquidity",
            0
        )
    )


st.markdown("---")


# ====================================
# EXECUTION SUMMARY
# ====================================

st.subheader(
    "Execution Summary"
)

st.json(
    st.session_state.execution_summary
)


st.markdown("---")


# ====================================
# FILLS
# ====================================

fills = (
    st.session_state.fills
)

st.subheader(
    "Recent Fills"
)

if len(fills) == 0:

    st.info(
        "No fills yet"
    )

else:

    st.table(
        fills[-10:]
    )


st.markdown("---")


# ====================================
# PNL DASHBOARD
# ====================================

st.subheader(
    "PnL Dashboard"
)

pnl_dashboard = (

    PnLDashboard(
        fills
    )
)

pnl_dashboard.render()


st.markdown("---")


# ====================================
# EXECUTION STATUS
# ====================================

execution_status = (
    st.session_state.execution_status
)

st.subheader(
    "Execution Status"
)

if execution_status["halted"]:

    st.error(

        f"HALTED | "

        f"{execution_status['reason']}"
    )

else:

    st.success(

        execution_status["status"]
    )


st.markdown("---")


# ====================================
# ALERTS
# ====================================

alerts = (
    st.session_state.alerts
)

st.subheader(
    "Alerts"
)

if len(alerts) == 0:

    st.success(
        "No Active Alerts"
    )

else:

    for alert in alerts[-10:]:

        st.warning(alert)


# ====================================
# FOOTER
# ====================================

st.caption(

    f"Runtime Mode: {RUNTIME_MODE} | "

    f"Data Mode: {DATA_MODE}"
)


# ====================================
# AUTO REFRESH
# ====================================

time.sleep(1)

st.rerun()