# Redpanda Connect Output Components Index

> Source: https://docs.redpanda.com/redpanda-connect/components/outputs/

## Overview

80+ output components covering cloud services, databases, message queues, APIs, and local file operations.

## Services (Messaging & Storage)

| Component | Description |
|-----------|-------------|
| `amqp_0_9` | AMQP 0.9.1 protocol (RabbitMQ) |
| `amqp_1` | AMQP 1.0 protocol |
| `aws_dynamodb` | AWS DynamoDB tables |
| `aws_kinesis` | AWS Kinesis Data Streams |
| `aws_kinesis_firehose` | AWS Kinesis Firehose |
| `aws_s3` | AWS S3 bucket objects |
| `aws_sns` | AWS SNS topics |
| `aws_sqs` | AWS SQS queues |
| `azure_blob_storage` | Azure Blob Storage |
| `azure_data_lake_gen2` | Azure Data Lake Gen2 |
| `azure_queue_storage` | Azure Queue Storage |
| `azure_table_storage` | Azure Table Storage |
| `beanstalkd` | Beanstalkd work queues |
| `cache` | Write to cache resources |
| `cypher` | Neo4j Cypher queries |
| `discord` | Discord channel messages |
| `elasticsearch_v8` | Elasticsearch v8+ |
| `gcp_bigquery` | GCP BigQuery inserts |
| `gcp_cloud_storage` | GCP Cloud Storage |
| `gcp_pubsub` | GCP Pub/Sub topics |
| `hdfs` | Hadoop HDFS files |
| `mongodb` | MongoDB collections |
| `mqtt` | MQTT broker publishing |
| `nats` | NATS messaging |
| `nats_jetstream` | NATS JetStream |
| `nats_kv` | NATS Key-Value store |
| `nats_stream` | NATS Streaming |
| `nsq` | NSQ message queue |
| `opensearch` | OpenSearch indexing |
| `ockam_kafka` | Ockam-secured Kafka |
| `pulsar` | Apache Pulsar |
| `pusher` | Pusher channels |
| `questdb` | QuestDB time-series |
| `redis_hash` | Redis hash operations |
| `redis_list` | Redis list operations |
| `redis_pubsub` | Redis Pub/Sub |
| `redis_streams` | Redis Streams |
| `redpanda` | Redpanda/Kafka topics |
| `redpanda_common` | Redpanda with Schema Registry |
| `redpanda_migrator` | Cross-cluster migration |
| `snowflake` | Snowflake tables |
| `snowflake_streaming` | Snowflake Streaming API |
| `splunk` | Splunk HEC |
| `sql_insert` | SQL INSERT statements |
| `sql_raw` | Raw SQL execution |
| `timeplus` | Timeplus streaming |

## Utility Components

| Component | Description |
|-----------|-------------|
| `broker` | Fan-out to multiple outputs |
| `drop` | Discard messages |
| `drop_on` | Conditional message dropping |
| `dynamic` | Runtime-configurable outputs |
| `fallback` | Fallback on failure |
| `inproc` | In-process message passing |
| `reject` | Reject all messages |
| `reject_errored` | Reject only errored messages |
| `resource` | Reference output resources |
| `retry` | Retry failed outputs |
| `subprocess` | External process stdin |
| `switch` | Content-based routing |
| `sync_response` | Synchronous response |

## AI/Vector Database

| Component | Description |
|-----------|-------------|
| `cyborgdb` | CyborgDB vector store |
| `pinecone` | Pinecone vector database |
| `qdrant` | Qdrant vector database |

## Network

| Component | Description |
|-----------|-------------|
| `http_client` | HTTP requests |
| `http_server` | HTTP response serving |
| `nanomsg` | Nanomsg sockets |
| `sftp` | SFTP file uploads |
| `socket` | TCP/UDP sockets |
| `websocket` | WebSocket connections |
| `zmq4` | ZeroMQ sockets |

## Local/Filesystem

| Component | Description |
|-----------|-------------|
| `file` | Local file writing |
| `stdout` | Standard output stream |

## Social

| Component | Description |
|-----------|-------------|
| `slack_reaction` | Slack emoji reactions |

## Integration

| Component | Description |
|-----------|-------------|
| `couchbase` | Couchbase operations |
| `schema_registry` | Schema Registry publishing |
