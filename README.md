# Sample Data Generator

Generate realistic sample log data for various systems including Industrial Control Systems (Contoso Manufacturing), Windows, Cloud Manager (Fabrikam), and Hypervisor (Fabrikam).

## Features

- **Beautiful CLI** - Rich colored output with progress bars and status updates
- **Fast** - Generate thousands of log entries in seconds
- **uvx Compatible** - Run directly from URL with zero installation
- **Multiple Formats** - Support for syslog and Windows Event Log XML
- **Realistic Data** - Randomized but realistic log entries
- **Fictional Companies** - Uses fictional company names (Contoso, Fabrikam)

## Quick Start

### Run with uvx (Recommended)

Run directly from GitHub Pages without cloning:

```bash
uvx https://aronchick.github.io/sample-data/generate.py
```

### Run Locally

```bash
# Clone the repository
git clone https://github.com/aronchick/sample-data.git
cd sample-data

# Run with uv
uv run --script generate.py

# Or make it executable and run directly
chmod +x generate.py
./generate.py
```

## Usage

### Basic Usage

```bash
# Generate 10,000 industrial control system syslog entries (default)
uv run --script generate.py

# Generate Windows Event Logs
uv run --script generate.py windows

# Generate cloud manager logs
uv run --script generate.py cloud-mgr

# Generate hypervisor logs
uv run --script generate.py hypervisor
```

### Advanced Options

```bash
# Custom output file and line count
uv run --script generate.py industrial -o custom.log -n 50000

# Generate 100,000 Windows Event Logs
uv run --script generate.py windows -o windows-events.xml -n 100000

# Show help and all options
uv run --script generate.py --help
```

## Supported Log Types

### 1. Industrial Control Systems (Contoso Manufacturing)
Industrial control system syslog entries including:
- Port state changes
- CRC errors
- PLC communication loss
- Security alerts (port scans, login failures)

**Example output:**
```
<135>2025-11-19T21:46:04Z SWITCH-A1 NETWORK-DEVICE: \
    %PORT-5-LINK_STATE_CHANGE: Port G1/1 changed state to UP
```

### 2. Windows Event Logs (XML)
Windows Security and System event logs including:
- Logon/logoff events (4624, 4625, 4634)
- User account changes (4720, 4723, 4724)
- Authentication details

**Example output:**
```xml
<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <Provider Name="Microsoft-Windows-Security-Auditing" />
    <EventID>4624</EventID>
    <TimeCreated SystemTime="2025-11-19T21:46:17Z" />
    <Channel>Security</Channel>
    <Computer>WIN-SRV01.CONTOSO.LOCAL</Computer>
  </System>
  <EventData>
    <Data Name="SubjectUserName">ADMIN</Data>
    <Data Name="SubjectDomainName">CONTOSO</Data>
    <Data Name="LogonType">3</Data>
    <Data Name="IpAddress">10.0.0.50</Data>
    <Data Name="IpPort">3389</Data>
  </EventData>
</Event>
```

### 3. Cloud Manager (Fabrikam Cloud Manager)
Cloud-based virtual machine management operations:
- VM power operations
- VM migrations
- Snapshot creation
- Task tracking

**Example output:**
```
<134>2025-11-19T21:46:04Z FABRIKAM-CLOUD01.CONTOSO.LOCAL \
    cloudmgrd[12345]: [Originator@6876 sub=CloudTask opID=123-4567] \
    [User ADMIN@LOCAL] PowerOnVM_Task on APP-SRV01 (success), \
    TaskId=task-789012
```

### 4. Hypervisor (Fabrikam Hypervisor)
Hypervisor component logs:
- hvkernel events
- hostd operations
- mgmtd VM updates

**Example output:**
```
<134>2025-11-19T21:46:04Z FABRIKAM-HV01 hvkernel: cpu4: \
    StorageIO Cmd(0x12345678) from world 123456 to dev \
    "naa.6006016087654321" failed
```

## Output

The generator creates a file with the specified number of log entries:

```
Log Generator Configuration
   Source Type:    industrial
   Output File:    logs.out
   Lines:          10,000

  Generating industrial logs...  100% 10,000/10,000 0:00:02

Generation Complete
   Lines Generated:    10,000
   File Size:          1.20 MB (1,258,960 bytes)
   Output:             /path/to/logs.out
```

## Setting Up GitHub Pages

To host this on GitHub Pages and enable uvx execution from URL:

1. **Enable GitHub Pages:**
   - Go to your repository Settings
   - Navigate to Pages
   - Under "Source", select "Deploy from a branch"
   - Select the `main` branch and `/docs` folder
   - Click Save

2. **Access your page:**
   - Visit https://aronchick.github.io/sample-data/

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (for running the script)

The script automatically installs the `rich` library when run.

## Development

The script uses inline metadata (PEP 723) for dependency management:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich>=13.7.0",
# ]
# ///
```

This allows it to be run directly with `uv run --script` without a `pyproject.toml`.

## Migration from Bash

This replaces the original `generator.sh` bash script with a modern Python implementation featuring:

- Rich colored terminal output
- Progress bars and status updates
- Better error handling
- Type hints and documentation
- uvx compatibility for zero-install execution
- Cross-platform compatibility
- Uses fictional company names (Contoso, Fabrikam)

The original `generator.sh` is still available for reference.

## Fictional Company Names

This tool uses standard fictional company names for documentation and demos:

- **Contoso** - Used for the manufacturing/industrial domain and general corporate examples
- **Fabrikam** - Used for cloud and virtualization services

These are placeholder names commonly used in technical documentation and training materials to avoid using real company trademarks.

## License

This is a sample data generator for testing and development purposes.
