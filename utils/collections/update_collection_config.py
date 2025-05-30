from weaviate.classes.config import Reconfigure, PQEncoderType, PQEncoderDistribution, VectorFilterStrategy, ReplicationDeletionStrategy
import pandas as pd

# Get the current configuration of a collection
def get_collection_config(client, collection_name):
	print(f"get_collection_config is called")
	try:
		collection = client.collections.get(collection_name)
		config = collection.config.get()
		return config
	except Exception as e:
		raise Exception(f"Failed to get collection configuration: {str(e)}")

# Update the configuration of a collection (all mutable params)
def update_collection_config(client, collection_name, config_updates):
	print(f"update_collection_config is called")
	try:
		collection = client.collections.get(collection_name)
		update_config = {}

		# Description update
		if 'description' in config_updates:
			update_config['description'] = config_updates['description']

		# Inverted Index Config
		inverted_config_updates = {}
		if any(key in config_updates for key in ['bm25_b', 'bm25_k1', 'cleanup_interval_seconds', 'stopwords_additions', 'stopwords_preset', 'stopwords_removals']):
			if 'bm25_b' in config_updates:
				inverted_config_updates['bm25_b'] = config_updates['bm25_b']
			if 'bm25_k1' in config_updates:
				inverted_config_updates['bm25_k1'] = config_updates['bm25_k1']
			if 'cleanup_interval_seconds' in config_updates:
				inverted_config_updates['cleanup_interval_seconds'] = config_updates['cleanup_interval_seconds']
			if 'stopwords_additions' in config_updates:
				additions_str = config_updates['stopwords_additions']
				inverted_config_updates['stopwords_additions'] = [item.strip() for item in additions_str.split(',') if item.strip()]
			if 'stopwords_preset' in config_updates:
				inverted_config_updates['stopwords_preset'] = config_updates['stopwords_preset']
			if 'stopwords_removals' in config_updates:
				removals_str = config_updates['stopwords_removals']
				inverted_config_updates['stopwords_removals'] = [item.strip() for item in removals_str.split(',') if item.strip()]
			if inverted_config_updates:
				update_config['inverted_index_config'] = Reconfigure.inverted_index(**inverted_config_updates)

		# Multi-Tenancy Config
		multi_tenancy_config_updates = {}
		if any(key in config_updates for key in ['auto_tenant_creation', 'auto_tenant_activation']):
			if 'auto_tenant_creation' in config_updates:
				multi_tenancy_config_updates['auto_tenant_creation'] = config_updates['auto_tenant_creation']
			if 'auto_tenant_activation' in config_updates:
				multi_tenancy_config_updates['auto_tenant_activation'] = config_updates['auto_tenant_activation']
			if multi_tenancy_config_updates:
				update_config['multi_tenancy_config'] = Reconfigure.multi_tenancy(**multi_tenancy_config_updates)

		# Replication Config
		replication_config_updates = {}
		if any(key in config_updates for key in ['async_enabled', 'deletion_strategy']):
			if 'async_enabled' in config_updates:
				replication_config_updates['async_enabled'] = config_updates['async_enabled']
			if 'deletion_strategy' in config_updates:
				val = config_updates['deletion_strategy']
				if isinstance(val, ReplicationDeletionStrategy):
					replication_config_updates['deletion_strategy'] = val
				elif isinstance(val, str) and hasattr(ReplicationDeletionStrategy, val):
					replication_config_updates['deletion_strategy'] = getattr(ReplicationDeletionStrategy, val)
				else:
					raise Exception(f"Invalid ReplicationDeletionStrategy: {val}")
			if replication_config_updates:
				update_config['replication_config'] = Reconfigure.replication(**replication_config_updates)

		# HNSW Vector Index Config (with PQ quantizer only)
		hnsw_params = {}
		if 'dynamic_ef_factor' in config_updates:
			hnsw_params['dynamic_ef_factor'] = config_updates['dynamic_ef_factor']
		if 'dynamic_ef_min' in config_updates:
			hnsw_params['dynamic_ef_min'] = config_updates['dynamic_ef_min']
		if 'dynamic_ef_max' in config_updates:
			hnsw_params['dynamic_ef_max'] = config_updates['dynamic_ef_max']
		if 'filter_strategy' in config_updates:
			val = config_updates['filter_strategy']
			if isinstance(val, VectorFilterStrategy):
				hnsw_params['filter_strategy'] = val
			elif isinstance(val, str) and hasattr(VectorFilterStrategy, val):
				hnsw_params['filter_strategy'] = getattr(VectorFilterStrategy, val)
			else:
				raise Exception(f"Invalid VectorFilterStrategy: {val}")
		if 'flat_search_cutoff' in config_updates:
			hnsw_params['flat_search_cutoff'] = config_updates['flat_search_cutoff']
		if 'vector_cache_max_objects' in config_updates:
			hnsw_params['vector_cache_max_objects'] = config_updates['vector_cache_max_objects']

		# PQ quantizer params (only PQ is mutable)
		pq_keys = ['pq_enabled', 'pq_centroids', 'pq_segments', 'pq_training_limit', 'pq_encoder_type', 'pq_encoder_distribution']
		pq_present = any(k in config_updates for k in pq_keys)
		pq_config = None
		if pq_present:
			pq_kwargs = {}
			if 'pq_enabled' in config_updates:
				pq_kwargs['enabled'] = config_updates['pq_enabled']
			if 'pq_centroids' in config_updates:
				pq_kwargs['centroids'] = config_updates['pq_centroids']
			if 'pq_segments' in config_updates:
				pq_kwargs['segments'] = config_updates['pq_segments']
			if 'pq_training_limit' in config_updates:
				pq_kwargs['training_limit'] = config_updates['pq_training_limit']
			if 'pq_encoder_type' in config_updates:
				val = config_updates['pq_encoder_type']
				if isinstance(val, PQEncoderType):
					pq_kwargs['encoder_type'] = val
				elif isinstance(val, str) and hasattr(PQEncoderType, val):
					pq_kwargs['encoder_type'] = getattr(PQEncoderType, val)
				else:
					raise Exception(f"Invalid PQEncoderType: {val}")
			if 'pq_encoder_distribution' in config_updates:
				val = config_updates['pq_encoder_distribution']
				if isinstance(val, PQEncoderDistribution):
					pq_kwargs['encoder_distribution'] = val
				elif isinstance(val, str) and hasattr(PQEncoderDistribution, val):
					pq_kwargs['encoder_distribution'] = getattr(PQEncoderDistribution, val)
				else:
					raise Exception(f"Invalid PQEncoderDistribution: {val}")
			pq_config = Reconfigure.VectorIndex.Quantizer.pq(**pq_kwargs)
			hnsw_params['quantizer'] = pq_config

		if hnsw_params:
			update_config['vectorizer_config'] = Reconfigure.VectorIndex.hnsw(**hnsw_params)

		if update_config:
			collection.config.update(**update_config)
		return True
	except Exception as e:
		raise Exception(f"Failed to update collection configuration: {str(e)}")

# Convert and display collection configuration to a pandas DataFrame
def display_config_as_table(config):
	print(f"display_config_as_table is called")
	if config is None:
		return pd.DataFrame()
	flat_config = {}
	flat_config['Description'] = getattr(config, 'description', None)
	if hasattr(config, 'inverted_index_config') and config.inverted_index_config is not None:
		inverted = config.inverted_index_config
		flat_config.update({
			'BM25 B': getattr(inverted, 'bm25_b', None),
			'BM25 K1': getattr(inverted, 'bm25_k1', None),
			'Cleanup Interval (s)': getattr(inverted, 'cleanup_interval_seconds', None),
			'Stopwords Preset': getattr(inverted, 'stopwords_preset', None),
			'Stopwords Additions': ', '.join(getattr(inverted, 'stopwords_additions', []) if getattr(inverted, 'stopwords_additions', []) is not None else []),
			'Stopwords Removals': ', '.join(getattr(inverted, 'stopwords_removals', []) if getattr(inverted, 'stopwords_removals', []) is not None else []),
		})
	if hasattr(config, 'multi_tenancy_config') and config.multi_tenancy_config is not None:
		multi = config.multi_tenancy_config
		flat_config.update({
			'Auto Tenant Creation': getattr(multi, 'auto_tenant_creation', None),
			'Auto Tenant Activation': getattr(multi, 'auto_tenant_activation', None)
		})
	if hasattr(config, 'replication_config') and config.replication_config is not None:
		repl = config.replication_config
		deletion_strategy_val = getattr(repl, 'deletion_strategy', None)
		flat_config['Deletion Strategy'] = deletion_strategy_val.name if deletion_strategy_val is not None else None
		flat_config['Async Enabled'] = getattr(repl, 'async_enabled', None)
	if hasattr(config, 'vectorizer_config') and config.vectorizer_config is not None:
		vector = config.vectorizer_config
		vector_index_type = getattr(vector, 'type', None)
		flat_config['Vector Index Type'] = vector_index_type
		flat_config['Vector Cache Max Objects'] = getattr(vector, 'vector_cache_max_objects', None)
		if vector_index_type == 'hnsw':
			flat_config.update({
				'Dynamic EF Factor': getattr(vector, 'dynamic_ef_factor', None),
				'Dynamic EF Min': getattr(vector, 'dynamic_ef_min', None),
				'Dynamic EF Max': getattr(vector, 'dynamic_ef_max', None),
				'Filter Strategy': getattr(vector, 'filter_strategy', None).name if getattr(vector, 'filter_strategy', None) is not None else None,
				'Flat Search Cutoff': getattr(vector, 'flat_search_cutoff', None),
			})
			if hasattr(vector, 'quantizer') and vector.quantizer is not None:
				quantizer = vector.quantizer
				if getattr(quantizer, 'type', None) == 'pq':
					flat_config['PQ Enabled'] = getattr(quantizer, 'enabled', None)
					flat_config['PQ Centroids'] = getattr(quantizer, 'centroids', None)
					flat_config['PQ Segments'] = getattr(quantizer, 'segments', None)
					flat_config['PQ Training Limit'] = getattr(quantizer, 'training_limit', None)
					if hasattr(quantizer, 'encoder') and quantizer.encoder is not None:
						flat_config['PQ Encoder Type'] = getattr(quantizer.encoder, 'type', None)
						flat_config['PQ Encoder Distribution'] = getattr(quantizer.encoder, 'distribution', None)
	df = pd.DataFrame([flat_config])
	return df 
