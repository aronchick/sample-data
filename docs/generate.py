#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich>=13.7.0",
# ]
# ///
"""
Sample Data Generator - Generate sample log data for various systems.

This tool generates realistic sample log data for testing and development:
- Industrial Control System syslog entries (Contoso Manufacturing)
- Windows Event Logs (XML format)
- Cloud Management syslog entries (Fabrikam Cloud Manager)
- Hypervisor syslog entries (Fabrikam Hypervisor)
"""

import argparse
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

console = Console()

SourceType = Literal["industrial", "windows", "cloud-mgr", "hypervisor"]


def now_ts() -> str:
    """Return current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def random_elem(arr: list[str]) -> str:
    """Return a random element from the array."""
    return random.choice(arr)


# ================================================
# Industrial Control System - syslog (Contoso Manufacturing)
# ================================================
def generate_industrial_syslog_line() -> str:
    """Generate an industrial control system syslog entry."""
    ts = now_ts()
    host = random_elem(["SWITCH-A1", "SWITCH-B2", "ROUTER-C3", "GATEWAY-D4"])
    severity = random_elem(["5", "4", "3"])
    facility = "13"

    ports = ["1", "2", "3", "4", "5", "6", "G1/1", "G1/2"]
    protos = ["PROFINET", "MODBUS", "DNP3", "IEC-104"]
    src_ips = ["10.0.0.10", "10.0.1.20", "10.0.2.30"]
    dst_ips = ["10.10.10.1", "10.10.20.1", "172.16.0.50"]
    states = ["UP", "DOWN", "ERR_DISABLED", "BLOCKING"]
    alerts = [
        f"%SEC-4-PORT_SCAN_DETECTED: Potential scan from "
        f"{src_ips[0]} to {dst_ips[0]} on {protos[0]}",
        f"%AUTH-3-LOGIN_FAILED: User 'USER1' failed login from "
        f"{src_ips[1]} via SSH",
        f"%AUTH-5-LOGIN_SUCCESS: User 'ADMIN' logged in from "
        f"{src_ips[2]} via HTTPS",
    ]

    msg_type = random.randint(0, 3)
    if msg_type == 0:
        port = random_elem(ports)
        state = random_elem(states)
        msg = (
            f"%PORT-5-LINK_STATE_CHANGE: Port {port} changed state "
            f"to {state}"
        )
    elif msg_type == 1:
        port = random_elem(ports)
        errors = random.randint(0, 99)
        msg = f"%PORT-4-ERRORS: CRC errors detected on port {port} "
        msg += f"(errors={errors})"
    elif msg_type == 2:
        dst_ip = random_elem(dst_ips)
        proto = random_elem(protos)
        msg = (
            f"%IND-3-PLC_COMM_LOSS: Lost communication with PLC at "
            f"{dst_ip} over {proto}"
        )
    else:
        msg = random_elem(alerts)

    return f"<{facility}{severity}>{ts} {host} NETWORK-DEVICE: {msg}"


# ================================================
# Windows Event Logs - XML
# ================================================
def generate_windows_event_xml() -> str:
    """Generate a Windows Event Log XML entry."""
    ts = now_ts()
    user = random_elem(["USER1", "USER2", "ADMIN", "SERVICE1"])
    event_id = random_elem(["4624", "4625", "4634", "4720", "4723", "4724"])
    logon_type = random_elem(["2", "3", "10"])
    ip = random_elem(["10.0.0.50", "10.0.1.77", "192.168.1.10"])
    host = random_elem(["WIN-SRV01", "WIN-SRV02", "WIN-DC01"])
    channel = random_elem(["Security", "System"])
    port = 1024 + random.randint(0, 39999)

    return f"""<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <Provider Name="Microsoft-Windows-Security-Auditing" />
    <EventID>{event_id}</EventID>
    <TimeCreated SystemTime="{ts}" />
    <Channel>{channel}</Channel>
    <Computer>{host}.CONTOSO.LOCAL</Computer>
  </System>
  <EventData>
    <Data Name="SubjectUserName">{user}</Data>
    <Data Name="SubjectDomainName">CONTOSO</Data>
    <Data Name="LogonType">{logon_type}</Data>
    <Data Name="IpAddress">{ip}</Data>
    <Data Name="IpPort">{port}</Data>
  </EventData>
</Event>
"""


# ================================================
# Cloud Manager - syslog (Fabrikam Cloud Manager)
# ================================================
def generate_cloud_mgr_syslog_line() -> str:
    """Generate a cloud management syslog entry."""
    ts = now_ts()
    host = random_elem(
        ["FABRIKAM-CLOUD01.CONTOSO.LOCAL", "FABRIKAM-CLOUD02.CONTOSO.LOCAL"]
    )
    vm = random_elem(["APP-SRV01", "APP-SRV02", "DB-SRV01", "WEB-SRV01"])
    user = random_elem(["ADMIN@LOCAL", "SERVICE-ACCT@LOCAL"])
    action = random_elem(
        [
            "PowerOnVM_Task",
            "PowerOffVM_Task",
            "MigrateVM_Task",
            "CreateSnapshot_Task",
        ]
    )
    status = random_elem(["success", "queued", "running", "error"])

    task_id = f"task-{random.randint(0, 999998)}"
    op_id = f"{random.randint(0, 998)}-{random.randint(0, 9999):04d}"
    pid = 10000 + random.randint(0, 4999)

    return (
        f"<134>{ts} {host} cloudmgrd[{pid}]: "
        f"[Originator@6876 sub=CloudTask opID={op_id}] "
        f"[User {user}] {action} on {vm} ({status}), TaskId={task_id}"
    )


# ================================================
# Hypervisor - syslog (Fabrikam Hypervisor)
# ================================================
def generate_hypervisor_syslog_line() -> str:
    """Generate a hypervisor syslog entry."""
    ts = now_ts()
    host = random_elem(
        ["FABRIKAM-HV01", "FABRIKAM-HV02", "FABRIKAM-EDGE01"]
    )
    component = random_elem(["hvkernel", "hostd", "mgmtd"])

    if component == "hvkernel":
        cpu = random.randint(0, 15)
        cmd = random.randint(0, 2**32 - 1)
        world = random.randint(0, 299999)
        dev = random.randint(0, 2**32 - 1)
        msg = (
            f"cpu{cpu}: StorageIO Cmd(0x{cmd:08x}) from "
            f"world {world} to dev \"naa.60060160{dev:08x}\" failed"
        )
    elif component == "hostd":
        pid = random.randint(1000, 99999)
        msg = (
            f"hostd[{pid}]: Event: User root@127.0.0.1 logged in "
            f"via Console"
        )
    else:  # mgmtd
        pid = random.randint(1000, 99999)
        msg = f"mgmtd[{pid}]: VM 'APP-SRV01' config updated"

    return f"<134>{ts} {host} {component}: {msg}"


# ================================================
# Generator functions by type
# ================================================
def generate_logs(
    source: SourceType,
    outfile: Path,
    lines: int,
) -> None:
    """
    Generate log entries and write them to the output file or stdout.

    Args:
        source: Type of log source (industrial, windows, cloud-mgr,
                hypervisor)
        outfile: Path to the output file (use Path('-') for stdout)
        lines: Number of log lines to generate
    """
    generators = {
        "industrial": generate_industrial_syslog_line,
        "windows": generate_windows_event_xml,
        "cloud-mgr": generate_cloud_mgr_syslog_line,
        "hypervisor": generate_hypervisor_syslog_line,
    }

    generator = generators[source]
    use_stdout = str(outfile) == "-"

    # Show configuration only if not streaming to stdout
    if not use_stdout:
        config_table = Table(show_header=False, box=None, padding=(0, 2))
        config_table.add_column(style="cyan bold")
        config_table.add_column(style="white")
        config_table.add_row("Source Type:", source)
        config_table.add_row("Output File:", str(outfile))
        config_table.add_row("Lines:", f"{lines:,}")

        console.print()
        console.print(
            Panel(
                config_table,
                title="[bold cyan]Log Generator Configuration[/bold cyan]",
                border_style="cyan",
            )
        )
        console.print()

    # Generate logs
    if use_stdout:
        # Stream directly to stdout without progress bar
        import sys

        for i in range(lines):
            line = generator()
            sys.stdout.write(line)
            if source == "windows":
                sys.stdout.write("\n")
            sys.stdout.write("\n")
            sys.stdout.flush()
    else:
        # Write to file with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[cyan]{task.completed:,}/{task.total:,} lines[/cyan]"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Generating {source} logs...", total=lines
            )

            with outfile.open("w") as f:
                for i in range(lines):
                    line = generator()
                    f.write(line)
                    if source == "windows":
                        f.write("\n")
                    f.write("\n")

                    # Update progress every 100 lines to reduce overhead
                    if i % 100 == 0 or i == lines - 1:
                        progress.update(task, completed=i + 1)

        # Show summary
        file_size = outfile.stat().st_size
        size_mb = file_size / (1024 * 1024)

        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column(style="green bold")
        summary_table.add_column(style="white")
        summary_table.add_row("Lines Generated:", f"{lines:,}")
        summary_table.add_row(
            "File Size:", f"{size_mb:.2f} MB ({file_size:,} bytes)"
        )
        summary_table.add_row("Output:", str(outfile.absolute()))

        console.print()
        console.print(
            Panel(
                summary_table,
                title="[bold green]\u2713 Generation Complete[/bold green]",
                border_style="green",
            )
        )
        console.print()


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate sample log data for various systems "
            "(Industrial, Windows, Cloud Manager, Hypervisor)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10,000 industrial control system syslog entries (default)
  uv run https://aronchick.github.io/sample-data/generate.py

  # Generate Windows Event Logs
  uv run https://aronchick.github.io/sample-data/generate.py windows

  # Generate 50,000 cloud manager logs to custom file
  uv run https://aronchick.github.io/sample-data/generate.py \\
      cloud-mgr -o cloud.log -n 50000

  # Generate hypervisor logs
  uv run https://aronchick.github.io/sample-data/generate.py \\
      hypervisor -o hypervisor.log

  # Stream industrial logs to stdout (for piping)
  uv run https://aronchick.github.io/sample-data/generate.py \\
      industrial -o - -n 100

Available source types:
  industrial  - Industrial control system syslog (Contoso Manufacturing)
  windows     - Windows Event Logs (XML format)
  cloud-mgr   - Cloud management syslog (Fabrikam Cloud Manager)
  hypervisor  - Hypervisor syslog (Fabrikam Hypervisor)
        """,
    )

    parser.add_argument(
        "source",
        nargs="?",
        default="industrial",
        choices=["industrial", "windows", "cloud-mgr", "hypervisor"],
        help="Log source type (default: industrial)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("logs.out"),
        help="Output file path, use '-' for stdout (default: logs.out)",
    )

    parser.add_argument(
        "-n",
        "--lines",
        type=int,
        default=10000,
        help="Number of log lines to generate (default: 10000)",
    )

    return parser


def main() -> int:
    """Main entry point for the log generator."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        generate_logs(
            source=args.source,
            outfile=args.output,
            lines=args.lines,
        )
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}", style="red")
        return 1


if __name__ == "__main__":
    sys.exit(main())
