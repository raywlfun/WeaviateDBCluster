import streamlit as st

# Update the side bar labels on the fly
def update_side_bar_labels():
    print("update_side_bar_labels called")
    if not st.session_state.get("client_ready"):
        st.warning("Please Establish a connection to Weaviate on the side bar")
    else:
        st.sidebar.info("Connection Status: ✅")
        st.sidebar.info(f"Current Connected Endpoint: {st.session_state.get('active_endpoint', 'N/A')}")
        st.sidebar.info(f"Client Version: {st.session_state.get('client_version', 'N/A')}")
        st.sidebar.info(f"Server Version: {st.session_state.get('server_version', 'N/A')}")

# Clear the session state
def clear_session_state():
	print("Session state cleared!")
	st.cache_data.clear()
	for key in st.session_state.keys():
		del st.session_state[key]
