# Expanso Quick Start Guide

> Source: https://docs.expanso.io/getting-started/quick-start/

## Overview

Expanso enables deployment of intelligent data pipelines at the edge. The platform reduces bandwidth, latency, and costs by processing data where it's generated, controlled through a central SaaS interface.

## Getting Started in 5 Minutes

### Prerequisites
- Computer running Linux, macOS, or Windows
- Internet connection
- Terminal access

### Step 1: Create Expanso Cloud Account

Visit [cloud.expanso.io](https://cloud.expanso.io), sign up, verify your email, and log in.

### Step 2: Create Your First Network

A network logically groups nodes working together:

1. Click **Create Network** on the dashboard
2. Enter name: `my-first-network`
3. Optionally add description: "My first Expanso network"
4. Click **Create**

### Step 3: Deploy a Node

Nodes are edge agents executing data pipelines on your infrastructure.

#### Generate Bootstrap Token

1. In network view, click **Add Agent**
2. Copy the bootstrap token
3. Keep window open for install command

#### Install the Edge Agent

**Linux/macOS:**
```bash
# Download and install
curl -fsSL https://get.expanso.io/edge/install.sh | bash

# Verify installation
expanso-edge version

# Bootstrap the agent with your token
expanso-edge bootstrap --token YOUR_BOOTSTRAP_TOKEN
```

**Windows Options:**

Option 1 - Docker (Recommended):
```bash
docker run `
  -e EXPANSO_EDGE_BOOTSTRAP_TOKEN=YOUR_BOOTSTRAP_TOKEN `
  ghcr.io/expanso-io/expanso-edge:nightly
```

Option 2 - WSL2:
```bash
curl -fsSL https://get.expanso.io/edge/install.sh | bash
expanso-edge bootstrap --token YOUR_BOOTSTRAP_TOKEN
```

Option 3 - Manual Install: Contact support@expanso.io for binary download.

#### Verify Node Connection

1. Return to Expanso Cloud
2. Node should appear in network overview or Nodes tab
3. Note the node's name (usually hostname)

### Step 4: Build Your First Pipeline

Create a pipeline reading logs and sending them to output.

#### Create the Pipeline

1. Open **Pipelines** tab
2. Click **Create Pipeline**
3. Name it: `log-processor`
4. Click **Open Pipeline Builder**

#### Configure the Input

1. Click **Add Input**
2. Select **File**
3. Configure:
```yaml
paths:
  - /var/log/app/*.log
```
4. Click **Save**

#### Add a Processor (Optional)

Add filter for error logs only:

1. Click to add processor after input
2. Select **Mapping** (Bloblang)
3. Add transformation:
```bloblang
# Only pass through if log contains "ERROR"
root = if this.message.contains("ERROR") {
  this
} else {
  deleted()
}
```
4. Click **Save**

#### Configure the Output

Output to STDOUT for viewing:

1. Click **Add Output**
2. Select **STDOUT**
3. Configure format:
```yaml
codec: lines
```
4. Click **Save**

#### Visual Pipeline Structure

```
[File Input] → [Filter (ERROR only)] → [STDOUT Output]
```

### Step 5: Deploy and Monitor

#### Deploy the Pipeline

1. Click **Save** in pipeline builder
2. Name and describe the pipeline
3. Select target agents or use label selectors
4. Click **Confirm Deploy**

Pipeline deploys to node(s) within seconds.

#### Monitor Your Pipeline

1. Go to **Monitoring** section
2. View pipeline metrics:
   - **Messages/sec**: Throughput
   - **Bytes/sec**: Data volume
   - **Errors**: Processing errors
   - **Latency**: Processing time
3. Click pipeline for detailed metrics
4. View logs for actual data flowing through

## Key Features

**200+ Pre-built Components** including:
- Inputs: Kafka, HTTP, files
- Processors: Transformations, filtering, PII masking, aggregations
- Outputs: S3, Snowflake, Datadog, Splunk

**Pipeline Building Options:**
- Drag-and-drop visual builder (no coding required)
- YAML configuration
- Bloblang transformation language

**AI/ML Support:**
Running ONNX, TensorFlow Lite, and other models as native pipeline steps for low-latency inference.

**Governance Features:**
- PII detection and masking
- Policy enforcement at edge
- RBAC and SSO integration
- Comprehensive audit trails

## Testing Without Cloud

Use **Local Mode** to run pipelines standalone without cloud connection—ideal for development and testing.

## Troubleshooting

**Node Not Connecting:**
- Verify correct bootstrap token
- Check network connectivity to cloud.expanso.io
- Review agent logs: `expanso-edge logs`

**Pipeline Not Deploying:**
- Ensure node is online (green status)
- Check for configuration errors
- Review deployment logs in UI

**No Data Flowing:**
- Verify input source has data
- Check file paths and permissions
- Review processor logic for filtering
- Check agent logs for errors

## Next Steps

- Explore [Core Concepts](/getting-started/core-concepts)
- Browse [Components](/components) catalog
- Review [Use Cases](/use-cases) examples
- Connect real data sources (Kafka, HTTP, etc.)
- Transform data with Bloblang
- Deploy nodes across infrastructure
- Set up monitoring alerts and dashboards

**Support:** Contact support@expanso.io
