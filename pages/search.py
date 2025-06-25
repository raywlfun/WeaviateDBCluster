import streamlit as st
from utils.search.hybrid import hybrid_search
from utils.search.keyword import keyword_search
from utils.cluster.collection import list_collections
from utils.page_config import set_custom_page_config
from utils.sidebar.navigation import navigate
from utils.sidebar.helper import update_side_bar_labels

# Initialize session state variables
def initialize_session_state():
	print("initialize_session_state() called")

	if 'selected_collection' not in st.session_state:
		st.session_state.selected_collection = None
	if 'search_query' not in st.session_state:
		st.session_state.search_query = ""
	if 'search_alpha' not in st.session_state:
		st.session_state.search_alpha = 0.5
	if 'search_limit' not in st.session_state:
		st.session_state.search_limit = 3
	if 'search_type' not in st.session_state:
		st.session_state.search_type = "Hybrid"

# Display the search interface with parameter
def display_search_interface():
	print("display_search_interface() called")
	# Collection selection
	collections = list_collections(st.session_state.client)
	selected_collection = st.selectbox(
		"Select Collection",
		options=collections,
		index=collections.index(st.session_state.selected_collection) if st.session_state.selected_collection in collections else 0,
		help="Choose a collection to search in"
	)

	# Search type selection
	search_type = st.radio(
		"Search Type",
		options=["Hybrid", "Keyword"],
		horizontal=True,
		help="Choose between hybrid (vector + keyword) or keyword-only search"
	)

	# Search parameters
	query = st.text_input(
		"Search Query",
		value=st.session_state.search_query,
		help="Enter your search query"
	)

	col1, col2 = st.columns(2)
	with col1:
		if search_type == "Hybrid":
			alpha = st.number_input(
				"Alpha",
				min_value=0.0,
				max_value=1.0,
				value=st.session_state.search_alpha,
				step=0.1,
				help="Balance between vector and keyword search (0.0 to 1.0)"
			)
	with col2:
		limit = st.number_input(
			"Limit",
			min_value=1,
			max_value=100,
			value=st.session_state.search_limit,
			step=1,
			help="Maximum number of results to return"
		)

	# Search button
	search_button = st.button("Search")

	if search_button:
		# Update session state
		st.session_state.selected_collection = selected_collection
		st.session_state.search_query = query
		st.session_state.search_type = search_type
		if search_type == "Hybrid":
			st.session_state.search_alpha = alpha
		st.session_state.search_limit = limit

		# Perform search based on type
		if search_type == "Hybrid":
			success, message, df, time_taken = hybrid_search(
				st.session_state.client,
				selected_collection,
				query,
				alpha,
				limit
			)
		else:
			success, message, df, time_taken = keyword_search(
				st.session_state.client,
				selected_collection,
				query,
				limit
			)

		# Display results
		display_results(success, message, df, time_taken)

# Function to display results
def display_results(success: bool, message: str, df, time_taken: float):
	print("display_results() called")
	if success:
		# Create a container for the success message and timing
		col1, col2 = st.columns([3, 1])
		with col1:
			st.success(message)
		with col2:
			st.info(f"Query Time Taken: {time_taken/1000:.3f}s ({time_taken:.2f}ms - {time_taken/1000/60:.3f}m)")

		if not df.empty:
			st.dataframe(df, use_container_width=True)
	else:
		st.error(message)

def main():
	set_custom_page_config(page_title="Search")
	navigate()
	update_side_bar_labels()

	if st.session_state.get("client_ready"):
		initialize_session_state()

		st.markdown("""
		            Search across your collections using either hybrid or keyword search.
		            """)

		# Display search types in columns
		col1, col2 = st.columns(2)
		with col1:
			st.markdown("""
			            **Hybrid Search**:
			            - Combines vector and keyword search capabilities
			            - Adjust alpha to balance between vector and keyword search
			            - Best for semantic similarity and keyword matching
			            """)
		with col2:
			st.markdown("""
			            **Keyword Search (BM25)**:
			            - Pure keyword-based search
			            - Fast and efficient for exact matches
			            - No vector similarity involved
			            """)

		# Add tokenization information banner
		st.info("""
		        **Tokenization in Weaviate Search**
		        
		        Tokenization plays a crucial role in search functionality. Weaviate offers various tokenization options to configure how keyword searches and filters are performed for each property.
		        
		        To learn more about tokenization options and how they affect your search results, visit the [Weaviate Tokenization Documentation](https://weaviate.io/developers/academy/py/tokenization/options).
		        """)

		# Display search interface
		display_search_interface()
	else:
		st.warning("Please Establish a connection to Weaviate in Cluster page!")

if __name__ == "__main__":
	main()
