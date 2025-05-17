import streamlit as st
import json
from datetime import datetime, date
from utils.objects.update_object import get_object_in_collection, display_object_as_table, find_object_in_collection_on_nodes, get_object_in_tenant, find_object_in_tenant_on_nodes, update_object_properties
from utils.sidebar.navigation import navigate
from utils.sidebar.helper import update_side_bar_labels
from utils.cluster.collection import fetch_collection_config
from utils.page_config import set_custom_page_config

# Function to map schema properties to their types
def build_type_map_from_schema(schema):
	type_map = {}
	for prop in schema.get('properties', []):
		name = prop.get('name')
		data_type = prop.get('dataType', [])
		# Handle array types
		if isinstance(data_type, list) and len(data_type) == 1:
			dt = data_type[0]
			if dt.endswith('[]'):
				base_type = dt[:-2]
				type_map[name] = f'{base_type}_array'
			else:
				type_map[name] = dt
		elif isinstance(data_type, list) and len(data_type) > 1:
			# fallback: just use the first
			dt = data_type[0]
			if dt.endswith('[]'):
				base_type = dt[:-2]
				type_map[name] = f'{base_type}_array'
			else:
				type_map[name] = dt
		else:
			type_map[name] = str(data_type)
	return type_map

# Function to parse values based on their type
def parse_value_by_type(value, type_name):
	if type_name in ('text', 'string', 'uuid', 'geoCoordinates', 'phoneNumber', 'blob'):
		return str(value)
	elif type_name == 'boolean':
		if isinstance(value, bool):
			return value
		if isinstance(value, str):
			return value.lower() == 'true'
		return bool(value)
	elif type_name == 'int':
		try:
			return int(value)
		except Exception:
			return None
	elif type_name == 'number':
		try:
			return float(value)
		except Exception:
			return None
	elif type_name == 'date':
		# Accept both string and date/datetime
		if isinstance(value, (datetime, date)):
			return value.strftime('%Y-%m-%dT%H:%M:%S+00:00')
		elif isinstance(value, str):
			try:
				dt = datetime.fromisoformat(value)
				return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
			except Exception:
				return value
		else:
			return str(value)
	elif type_name.endswith('_array'):
		base_type = type_name[:-6]
		if isinstance(value, list):
			return [parse_value_by_type(v, base_type) for v in value]
		try:
			arr = json.loads(value)
			return [parse_value_by_type(v, base_type) for v in arr]
		except Exception:
			return []
	elif type_name == 'object':
		if isinstance(value, dict):
			return value
		try:
			return json.loads(value)
		except Exception:
			return {}
	else:
		return value

# Function to format values for display
def format_value_for_display(value, type_name):
	if type_name.endswith('_array') or type_name == 'object':
		return json.dumps(value, indent=2) if value else '[]' if type_name.endswith('_array') else '{}'
	elif type_name == 'date':
		if isinstance(value, str):
			try:
				return datetime.fromisoformat(value.replace('Z', '+00:00'))
			except Exception:
				return value
		elif isinstance(value, (datetime, date)):
			return value
		else:
			return value
	elif type_name == 'boolean':
		return bool(value)
	elif type_name == 'int':
		try:
			return int(value)
		except Exception:
			return 0
	elif type_name == 'number':
		try:
			return float(value)
		except Exception:
			return 0.0
	else:
		return str(value) if value is not None else ''

# Function to display the object as a table and edit its properties
def get_object_details():
	collection_name = st.text_input("Collection Name")
	object_uuid = st.text_input("Object UUID")
	with_tenant = st.checkbox("Tenant", value=False)

	tenant_name = None
	if with_tenant:
		tenant_name = st.text_input("Tenant Name")

	col1, col2 = st.columns(2)
	with col1:
		fetch_object_clicked = st.button("Fetch The Object", use_container_width=True)
	with col2:
		check_node_clicked = st.button("Check the Object on the Nodes (APIs)", use_container_width=True)

	# Initialize session state for edit mode and object data
	if 'edit_mode' not in st.session_state:
		st.session_state.edit_mode = False
	if 'current_object' not in st.session_state:
		st.session_state.current_object = None
	if 'object_display' not in st.session_state:
		st.session_state.object_display = None
	if 'type_map' not in st.session_state:
		st.session_state.type_map = None

	# Fetch schema and build type map
	if collection_name and (st.session_state.type_map is None or st.session_state.get('last_collection_name') != collection_name):
		# Try to get API key and endpoint from session state
		api_key = st.session_state.get('cluster_api_key')
		endpoint = st.session_state.get('cluster_endpoint')
		if api_key and endpoint:
			schema = fetch_collection_config(endpoint, api_key, collection_name)
			if schema and 'error' not in schema:
				st.session_state.type_map = build_type_map_from_schema(schema)
				st.session_state.last_collection_name = collection_name
			else:
				st.session_state.type_map = None
				st.session_state.last_collection_name = None

	# "Fetch Object"
	if fetch_object_clicked:
		if not collection_name.strip() or not object_uuid.strip():
			st.error("Please insert both Collection Name and UUID.")
			return

		try:
			# Fetch and display object
			if with_tenant and tenant_name:
				data_object = get_object_in_tenant(st.session_state.client, collection_name, object_uuid, tenant_name)
			else:
				data_object = get_object_in_collection(st.session_state.client, collection_name, object_uuid)

			if data_object:
				st.session_state.current_object = data_object
				st.session_state.object_display = display_object_as_table(data_object)
				st.session_state.edit_mode = False
			else:
				st.error(f"Object with UUID '{object_uuid}' not found.")
		except ValueError:
			st.error("Invalid UUID: Not a valid UUID or unable to extract it.")
		except Exception as e:
			st.error(f"An error occurred: {e}")

	# Display object data if available
	if st.session_state.object_display is not None:
		st.markdown("### Object Data")
		st.dataframe(st.session_state.object_display, use_container_width=True)

		# Add Edit button below the table
		if not st.session_state.edit_mode:
			if st.button("Edit Object", type="primary"):
				st.session_state.edit_mode = True
				st.rerun()

	# Edit mode UI
	if st.session_state.edit_mode and st.session_state.current_object:
		st.markdown("### Edit Object Properties")

		# Create form for editing properties
		with st.form("edit_object_form"):
			edited_properties = {}
			type_map = st.session_state.type_map or {}
			# Display and edit each property
			for key, value in st.session_state.current_object.properties.items():
				type_name = type_map.get(key, 'text')
				st.markdown(f"#### {key} ({type_name})")
				if type_name.endswith('_array') or type_name == 'object':
					edited_properties[key] = st.text_area(
						"Value (JSON Array/Object)",
						value=format_value_for_display(value, type_name),
						height=100,
						key=f"textarea_{key}"
					)
				elif type_name == 'date':
					dt_val = format_value_for_display(value, type_name)
					if isinstance(dt_val, (datetime, date)):
						edited_properties[key] = st.date_input(
							"Value (Date)",
							value=dt_val,
							key=f"date_{key}"
						)
					else:
						edited_properties[key] = st.text_input(
							"Value (Date String)",
							value=str(dt_val),
							key=f"date_{key}"
						)
				elif type_name == 'number':
					try:
						num_val = float(value)
					except Exception:
						num_val = 0.0
					edited_properties[key] = st.number_input(
						"Value (Number)",
						value=num_val,
						key=f"number_{key}"
					)
				elif type_name == 'int':
					try:
						int_val = int(value)
					except Exception:
						int_val = 0
					edited_properties[key] = st.number_input(
						"Value (Int)",
						value=int_val,
						step=1,
						key=f"int_{key}"
					)
				elif type_name == 'boolean':
					bool_val = bool(value)
					if isinstance(value, str):
						bool_val = value.lower() == 'true'
					edited_properties[key] = st.checkbox(
						"Value (Boolean)",
						value=bool_val,
						key=f"bool_{key}"
					)
				else: # text and fallback
					edited_properties[key] = st.text_input(
						"Value (Text)",
						value=str(value),
						key=f"text_{key}"
					)
			col1, col2 = st.columns(2)
			with col1:
				submitted = st.form_submit_button("Save Changes", use_container_width=True)
			with col2:
				cancel = st.form_submit_button("Cancel", use_container_width=True)
			if submitted:
				try:
					# Parse the values before updating
					parsed_properties = {}
					for key, value in edited_properties.items():
						type_name = type_map.get(key, 'text')
						parsed_properties[key] = parse_value_by_type(value, type_name)
					# Update the object
					if with_tenant and tenant_name:
						update_object_properties(
							st.session_state.client,
							collection_name,
							object_uuid,
							parsed_properties,
							tenant_name
						)
					else:
						update_object_properties(
							st.session_state.client,
							collection_name,
							object_uuid,
							parsed_properties
						)
					st.success("Object updated successfully!")
					st.session_state.edit_mode = False
					# Refresh the object display
					if with_tenant and tenant_name:
						data_object = get_object_in_tenant(st.session_state.client, collection_name, object_uuid, tenant_name)
					else:
						data_object = get_object_in_collection(st.session_state.client, collection_name, object_uuid)
					st.session_state.current_object = data_object
					st.session_state.object_display = display_object_as_table(data_object)
					st.rerun()
				except Exception as e:
					st.error(f"Failed to update object: {e}")
			if cancel:
				st.session_state.edit_mode = False
				st.rerun()
	# "Check Object on a Node"
	if check_node_clicked:
		if not collection_name.strip() or not object_uuid.strip():
			st.error("Please insert both Collection Name and UUID.")
			return
		try:
			# Fetch node data and display table
			api_key = st.session_state.cluster_api_key
			cluster_endpoint = st.session_state.cluster_endpoint
			if with_tenant and tenant_name:
				data_object = find_object_in_tenant_on_nodes(cluster_endpoint, api_key, collection_name, object_uuid, tenant_name)
			else:
				data_object = find_object_in_collection_on_nodes(cluster_endpoint, api_key, collection_name, object_uuid)
			node_df = data_object
			st.dataframe(node_df, use_container_width=True)
			st.text("✔ Found | ✖ Not Found | N/A The node does not exist (Hardcoded 11 nodes as maximum for now)")
		except Exception as e:
			st.error(f"An error occurred while checking the object on nodes: {e}")

def main():

	set_custom_page_config(page_title="Update Object")

	navigate()
	if st.session_state.get("client_ready"):
		update_side_bar_labels()
		get_object_details()
	else:
		st.warning("Please Establish a connection to Weaviate in Cluster page!")
if __name__ == "__main__":
	main()
