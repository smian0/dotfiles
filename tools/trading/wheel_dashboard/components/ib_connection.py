"""
IB Connection Component for Streamlit Dashboard

Provides UI for connecting to Interactive Brokers Gateway/TWS
"""

import asyncio
import streamlit as st
from typing import Optional


def init_ib_session_state():
    """Initialize IB connection state in Streamlit session"""
    if 'ib_manager' not in st.session_state:
        st.session_state.ib_manager = None
    if 'ib_connected' not in st.session_state:
        st.session_state.ib_connected = False
    if 'ib_connection_message' not in st.session_state:
        st.session_state.ib_connection_message = ""


def render_ib_connection_sidebar():
    """
    Render IB connection controls in sidebar

    Shows connection status and connect/disconnect buttons
    """
    init_ib_session_state()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 IB Connection")

    # Show current status
    if st.session_state.ib_connected and st.session_state.ib_manager:
        st.sidebar.success("✅ Connected to IB")

        if st.sidebar.button("Disconnect from IB"):
            try:
                if st.session_state.ib_manager:
                    st.session_state.ib_manager.disconnect()
                st.session_state.ib_manager = None
                st.session_state.ib_connected = False
                st.session_state.ib_connection_message = "Disconnected"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error disconnecting: {e}")

    else:
        st.sidebar.info("⚪ Not connected to IB")

        with st.sidebar.expander("Connect to IB Gateway/TWS"):
            # Connection settings
            host = st.text_input("Host", value="127.0.0.1", key="ib_host")
            port = st.number_input("Port", value=4001, min_value=1, max_value=65535, key="ib_port")
            client_id = st.number_input("Client ID", value=3, min_value=0, max_value=999, key="ib_client_id")
            use_paper = st.checkbox("Use Paper Trading", value=False, key="ib_paper")

            if st.button("Connect", key="ib_connect_btn"):
                try:
                    # Ensure event loop exists for ib_insync
                    try:
                        asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    # Lazy import IB modules (after event loop is set)
                    from connection import IBManager, IBConfig

                    # Create config
                    config = IBConfig(
                        host=host,
                        port=port,
                        client_id=client_id,
                        use_paper=use_paper
                    )

                    # Create manager
                    manager = IBManager(config)

                    # Connect
                    success, message = manager.connect()

                    if success:
                        st.session_state.ib_manager = manager
                        st.session_state.ib_connected = True
                        st.session_state.ib_connection_message = message
                        st.sidebar.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.sidebar.error(f"❌ Connection failed: {message}")

                except Exception as e:
                    st.sidebar.error(f"❌ Error: {e}")
                    st.sidebar.info("""
                    **Troubleshooting:**
                    - Ensure IB Gateway or TWS is running
                    - Check host/port settings
                    - Verify client ID is not in use
                    - Default port: 4001 (live), 7497 (paper TWS)
                    """)

    # Show connection message if available
    if st.session_state.ib_connection_message:
        st.sidebar.caption(st.session_state.ib_connection_message)


def get_ib_connection():
    """
    Get active IB connection from session state

    Returns:
        IB connection object or None
    """
    init_ib_session_state()

    if st.session_state.ib_connected and st.session_state.ib_manager:
        return st.session_state.ib_manager.get_connection()

    return None


def is_ib_connected() -> bool:
    """Check if IB is connected"""
    init_ib_session_state()
    return st.session_state.ib_connected and st.session_state.ib_manager is not None
