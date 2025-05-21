# Weaviate Cluster Operations

## Overview

Interact with and manage Weaviate Cluster operations. This app provides tools to inspect shards, view collections & tenants, explore schemas, analyze cluster statistics, and interact with objects.

<a href="https://weaviatecluster.streamlit.app/">
  Visit Weaviate Cluster WebApp
</a>

<img width="1698" alt="image" src="https://github.com/user-attachments/assets/a07260c9-78dd-477c-a3a5-bd94a96fe445" />

## Features

### Cluster Management
- **Shards & Nodes**
  - View shard details across nodes
  - View node details
  - Update read-only shards to READY status (⚠️ Admin API-Key required)

- **Collections & Tenants**
  - View collections and their tenants
  - Explore collection configurations
  - View schema configuration
  - Analyze cluster statistics and synchronization
  - View cluster metadata & modules
  - Analyze shard consistency
  - Force repair collection objects across nodes

#### Vectorization
- Support for OpenAI, Cohere, HuggingFace and JinaAI
- Add API keys for vectorization providers (optional)
- Vectorization during object updates
  
### Object Operations
- **Create**
  - Create new collections
  - Supported Vectorizers (OpenAI, Cohere, HuggingFace, JinaAI)
  - Batch upload data from CSV/JSON files

- **Read**
  - View object data in collections/tenants
  - Display data in tables including vectors
  - Download data as CSV files

- **Update**
  - Edit objects with vectorization
  - Download object data as CSV
  - Analyze object consistency across nodes (supports up to 11 nodes)

- **Delete**
  - Delete collections and tenants (⚠️ Admin API-Key required)
  - Batch deletion support for multiple collections/tenants

## Configuration

### How to Run It on Your Local Machine

**Prerequisites**

- Python 3.10 or higher
- pip installed

**Steps to Run**

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Shah91n/WeaviateCluster.git
    cd WeaviateCluster
    ```

2. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the app:**

    ```bash
    streamlit run streamlit_app.py
    ```

If you haven't already created a `requirements.txt` file, here's what it should look like:

```text
streamlit
weaviate-client
requests
pandas
```

Or You can also run the Weaviate Cluster using Docker. Follow the steps below to build the Docker image and run the container:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Shah91n/WeaviateCluster.git
    cd WeaviateCluster
    ```

2. **Build the Docker image:**

    ```bash
    docker build -t weaviateclusterapp:latest .
    ```

3. **Run the Docker container:**

    ```bash
    docker run -p 8501:8501 --add-host=localhost:host-gateway weaviateclusterapp
    ```

This will start the Weaviate Cluster, and you can access it by navigating to `http://localhost:8501` in your web browser.

### How to Run It on a Cloud Cluster

1. Provide the Weaviate endpoint.
2. Provide the API key.
3. Connect and enjoy!

### Notes

This is a personal project and is not officially approved by the Weaviate organization. While functional, the code may not follow all best practices for Python programming or Streamlit. Suggestions and improvements are welcome!

**USE AT YOUR OWN RISK**: While this tool is designed for cluster operation and analysis, there is always a possibility of unknown bugs. However, this tool is intended for read-only operations.

### Contributing

Contributions are welcome through pull requests! Suggestions for improvements and best practices are highly appreciated.
