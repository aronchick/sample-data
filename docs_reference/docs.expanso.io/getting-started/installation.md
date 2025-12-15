# Expanso Edge Installation Guide

> Source: https://docs.expanso.io/getting-started/installation/

## System Requirements

The platform has minimal resource needs:

- **CPU**: 0.5 cores
- **RAM**: 64 MB
- **Disk**: 150 MB

Requirements may scale based on pipeline configuration, data volume, and buffering needs.

**Supported Operating Systems:**
- Linux (kernel 3.10+)
- macOS (10.15+)
- Windows (10+)
- Docker

---

## Linux / macOS Installation

Install using the automated script:

```bash
curl -fsSL https://get.expanso.io/edge/install.sh | bash
```

Verify the installation succeeded:

```bash
expanso-edge version
```

Expected output: `Expanso Edge v1.x.x`

---

## Windows Installation

The automated PowerShell installer is not yet available. Choose from these options:

**Option 1: Docker (Recommended)**

```bash
docker pull ghcr.io/expanso-io/expanso-edge:nightly
docker run ghcr.io/expanso-io/expanso-edge:nightly version
```

**Option 2: Manual Installation**

Contact support@expanso.io for Windows binary download instructions.

**Option 3: Windows Subsystem for Linux**

```bash
curl -fsSL https://get.expanso.io/edge/install.sh | bash
```

---

## Docker Deployment

```bash
docker pull ghcr.io/expanso-io/expanso-edge:nightly
docker run -d \
  --name expanso-edge \
  --restart unless-stopped \
  ghcr.io/expanso-io/expanso-edge:nightly run
```

---

## Kubernetes Deployment

**Step 1: Create a bootstrap token secret**

```bash
kubectl create secret generic expanso-bootstrap \
  --from-literal=token=YOUR_BOOTSTRAP_TOKEN
```

**Step 2: Deploy as a sidecar**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: your-app-image:latest
      - name: expanso-edge
        image: ghcr.io/expanso-io/expanso-edge:latest
        args:
          - bootstrap
          - --token
          - $(EXPANSO_EDGE_BOOTSTRAP_TOKEN)
          - run
        env:
          - name: EXPANSO_EDGE_BOOTSTRAP_TOKEN
            valueFrom:
              secretKeyRef:
                name: expanso-bootstrap
                key: token
        volumeMounts:
          - name: expanso-cache
            mountPath: /var/lib/expanso
      volumes:
      - name: expanso-cache
        emptyDir: {}
```

**Kubernetes Best Practices:**
- Store tokens in Kubernetes Secrets, never hardcode them
- Emit logs to stdout/stderr for native cluster integration
- Use `emptyDir` or `hostPath` volumes for file-based logging

---

## Running Expanso Edge

Start the edge node with:

```bash
expanso-edge run
```

You'll be prompted for a registration token from Expanso Cloud.

### Configuration Options

```bash
# Custom node name
expanso-edge run --name my-edge-node

# Load configuration from file
expanso-edge run --config /path/to/config.yaml

# Enable verbose logging
expanso-edge run --verbose

# Set specific log level
expanso-edge run --log-level debug
```

---

## Optional: expanso-cli Installation

The command-line interface is useful for:
- Local development workflows
- CI/CD automation
- Programmatic deployment
- API access without custom code

Install via:

```bash
curl -fsSL https://get.expanso.io/cli/install.sh | sh
```

Verify installation:

```bash
expanso-cli version
```

You don't need it for standalone deployments using `expanso-edge run --config`.

---

## Next Steps

- Explore the [Quick Start](/getting-started/quick-start) guide
- Review [Core Concepts](/getting-started/core-concepts)
- Browse available [Components](/components)
- Try [Local Mode](/getting-started/local-mode) for development
