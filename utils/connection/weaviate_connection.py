import weaviate
import atexit
from weaviate.config import AdditionalConfig, Timeout

_client = None

# Connect to Weaviate server
def get_weaviate_client(cluster_endpoint=None, cluster_api_key=None, use_local=False, vectorizer_integration_keys=None, use_custom=False, http_host_endpoint=None, http_port_endpoint=None, grpc_host_endpoint=None, grpc_port_endpoint=None, custom_secure=False):
	print("get_weaviate_client() called")
	global _client
	if _client is None:
		headers = vectorizer_integration_keys if vectorizer_integration_keys else {}

		if use_local:
			_client = weaviate.connect_to_local(
				auth_credentials=weaviate.auth.AuthApiKey(cluster_api_key),
				port=http_port_endpoint,
				grpc_port=grpc_port_endpoint,
				skip_init_checks=True,
				additional_config=AdditionalConfig(
					timeout=Timeout(init=90, query=900, insert=900)
				),
				headers=headers
			)
		elif use_custom:
			_client = weaviate.connect_to_custom(
				http_host=http_host_endpoint,
				http_port=http_port_endpoint,
				http_secure=custom_secure,
				grpc_host=grpc_host_endpoint,
				grpc_port=grpc_port_endpoint,
				grpc_secure=custom_secure,
				auth_credentials=weaviate.auth.AuthApiKey(cluster_api_key),
				skip_init_checks=True,
				additional_config=AdditionalConfig(
					timeout=Timeout(init=90, query=900, insert=900)
				),
				headers=headers
			)
		else:
			_client = weaviate.connect_to_weaviate_cloud(
				cluster_url=cluster_endpoint,
				auth_credentials=weaviate.auth.AuthApiKey(cluster_api_key),
				skip_init_checks=True,
				additional_config=AdditionalConfig(
					timeout=Timeout(init=90, query=900, insert=900)
				),
				headers=headers
			)
		atexit.register(close_weaviate_client)
	return _client

# Close the Weaviate client connection
def close_weaviate_client():
	print("close_weaviate_client() called")
	global _client
	if _client:
		_client.close()
		_client = None

# Get Weaviate Server & Client status and version
def status(client):
	print("status() called")
	try:
		ready = client.is_ready()
		server_version = client.get_meta()["version"]
		client_version = weaviate.__version__
		return ready, server_version, client_version
	except Exception as e:
		print(f"Error: {e}")
		return False, "N/A", "N/A"
