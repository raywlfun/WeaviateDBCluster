import streamlit as st
from utils.connection.weaviate_connection import get_weaviate_client, status

# This function initializes the Weaviate client and sets the session state variables.
def initialize_client(cluster_endpoint, cluster_api_key, use_local=False, vectorizer_integration_keys=None):
	print("Initializing Weaviate Client...")
	try:
		client = get_weaviate_client(cluster_endpoint, cluster_api_key, use_local, vectorizer_integration_keys)
		st.session_state.client = client
		ready, server_version, client_version = status(client)
		st.session_state.client_ready = ready
		st.session_state.server_version = server_version
		st.session_state.client_version = client_version
		st.session_state.cluster_endpoint = cluster_endpoint if not use_local else "http://localhost:8080"
		st.session_state.cluster_api_key = cluster_api_key
		st.session_state.vectorizer_integration_keys = vectorizer_integration_keys
		return True
	except Exception as e:
		st.sidebar.error(f"Connection Error: {e}")
		st.session_state.client = None
		st.session_state.client_ready = False
		return False
