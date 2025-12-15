# Redpanda Connect Input Components Index

> Source: https://docs.redpanda.com/redpanda-connect/components/inputs/

## Overview

80+ input components covering messaging systems, databases, cloud platforms, and file-based sources.

## Services (Messaging & Storage)

| Component | Description |
|-----------|-------------|
| `amqp_0_9` | AMQP 0.9.1 protocol (RabbitMQ) |
| `amqp_1` | AMQP 1.0 protocol |
| `aws_kinesis` | AWS Kinesis Data Streams |
| `aws_s3` | AWS S3 bucket objects |
| `aws_sqs` | AWS SQS queues |
| `azure_blob_storage` | Azure Blob Storage containers |
| `azure_queue_storage` | Azure Queue Storage |
| `azure_table_storage` | Azure Table Storage |
| `cassandra` | Apache Cassandra queries |
| `beanstalkd` | Beanstalkd work queues |
| `discord` | Discord bot messages |
| `gcp_bigquery_select` | GCP BigQuery queries |
| `gcp_cloud_storage` | GCP Cloud Storage buckets |
| `gcp_pubsub` | GCP Pub/Sub subscriptions |
| `gcp_spanner_cdc` | GCP Spanner change data capture |
| `git` | Git repository files |
| `hdfs` | Hadoop HDFS files |
| `mongodb` | MongoDB collections |
| `mongodb_cdc` | MongoDB change streams |
| `mqtt` | MQTT broker subscriptions |
| `mysql_cdc` | MySQL change data capture |
| `microsoft_sql_server_cdc` | SQL Server change data capture |
| `nats` | NATS messaging |
| `nats_jetstream` | NATS JetStream |
| `nats_kv` | NATS Key-Value store |
| `nats_stream` | NATS Streaming |
| `nsq` | NSQ message queue |
| `ockam_kafka` | Ockam-secured Kafka |
| `postgres_cdc` | PostgreSQL change data capture |
| `pulsar` | Apache Pulsar |
| `redis_pubsub` | Redis Pub/Sub |
| `redis_scan` | Redis key scanning |
| `redis_list` | Redis list operations |
| `redis_streams` | Redis Streams |
| `redpanda` | Redpanda/Kafka topics |
| `redpanda_common` | Redpanda with Schema Registry |
| `redpanda_migrator` | Cross-cluster migration |
| `spicedb_watch` | SpiceDB permission changes |
| `splunk` | Splunk data |
| `sql_raw` | Raw SQL queries |
| `sql_select` | Structured SQL SELECT |
| `tigerbeetle_cdc` | TigerBeetle CDC |
| `timeplus` | Timeplus streaming |
| `twitter` | X/Twitter API |

## Utility Components

| Component | Description |
|-----------|-------------|
| `batched` | Batch messages from child input |
| `broker` | Fan-in from multiple inputs |
| `dynamic` | Runtime-configurable inputs |
| `generate` | Generate synthetic messages |
| `inproc` | In-process message passing |
| `read_until` | Conditional input termination |
| `resource` | Reference input resources |
| `sequence` | Sequential input chaining |
| `subprocess` | External process stdout |

## Local/Filesystem

| Component | Description |
|-----------|-------------|
| `csv` | CSV file parsing |
| `file` | Local file reading |
| `parquet` | Parquet file reading |
| `stdin` | Standard input stream |

## Network

| Component | Description |
|-----------|-------------|
| `http_client` | HTTP polling/requests |
| `http_server` | HTTP webhook receiver |
| `nanomsg` | Nanomsg sockets |
| `sftp` | SFTP file downloads |
| `socket` | TCP/UDP sockets |
| `socket_server` | TCP/UDP server |
| `websocket` | WebSocket connections |
| `zmq4` | ZeroMQ sockets |

## Integration

| Component | Description |
|-----------|-------------|
| `cockroachdb` | CockroachDB queries |
| `schema_registry` | Schema Registry lookups |
