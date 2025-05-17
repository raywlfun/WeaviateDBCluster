# functions to delete collections and tenants from collections in Weaviate
def delete_collections(client, collection_names):
	try:
		client.collections.delete(collection_names)
		return True, f"Successfully deleted collections: {', '.join(collection_names if isinstance(collection_names, list) else [collection_names])}"
	except Exception as e:
		return False, f"Error deleting collections: {str(e)}"

def delete_tenants_from_collection(client, collection_name, tenant_names):
	try:
		collection = client.collections.get(collection_name)
		collection.tenants.remove(tenant_names)
		return True, f"Successfully deleted tenants: {', '.join(tenant_names)} from collection {collection_name}"
	except Exception as e:
		return False, f"Error deleting tenants from collection {collection_name}: {str(e)}"
