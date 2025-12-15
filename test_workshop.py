#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich>=13.7.0",
#     "psycopg2-binary>=2.9.9",
#     "pymysql>=1.1.0",
# ]
# ///
"""
Test script for Bad Data Workshop.

Runs the workshop setup and teardown against Docker containers
to verify everything works correctly.

Usage:
    # Start containers, run tests, stop containers
    uv run --script test_workshop.py

    # Test only (containers must be running)
    uv run --script test_workshop.py --no-docker

    # Test specific database only
    uv run --script test_workshop.py --db postgres
    uv run --script test_workshop.py --db mysql
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from typing import Literal

from rich.console import Console
from rich.panel import Panel

console = Console()

# Docker connection settings
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "workshop",
    "user": "workshop",
    "password": "workshop123",
}

MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "workshop",
    "user": "workshop",
    "password": "workshop123",
}


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        console.print(f"[red]Command failed:[/red]\n{result.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def check_docker_running() -> bool:
    """Check if Docker daemon is running."""
    result = subprocess.run(
        ["docker", "ps"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def start_docker_containers() -> None:
    """Start Docker Compose containers."""
    console.print("\n[cyan]Starting Docker containers...[/cyan]")
    run_command(["docker", "compose", "up", "-d"])
    console.print("[green]✓ Containers started[/green]")


def stop_docker_containers() -> None:
    """Stop and remove Docker Compose containers."""
    console.print("\n[cyan]Stopping Docker containers...[/cyan]")
    run_command(["docker", "compose", "down", "-v"], check=False)
    console.print("[green]✓ Containers stopped[/green]")


def wait_for_postgres(max_wait: int = 60) -> bool:
    """Wait for PostgreSQL to be ready."""
    import psycopg2

    console.print("[cyan]Waiting for PostgreSQL...[/cyan]")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            conn.close()
            console.print("[green]✓ PostgreSQL is ready[/green]")
            return True
        except psycopg2.OperationalError:
            time.sleep(1)
    console.print("[red]✗ PostgreSQL not ready after {max_wait}s[/red]")
    return False


def wait_for_mysql(max_wait: int = 90) -> bool:
    """Wait for MySQL to be ready."""
    import pymysql

    console.print("[cyan]Waiting for MySQL...[/cyan]")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            conn = pymysql.connect(**MYSQL_CONFIG)
            conn.close()
            console.print("[green]✓ MySQL is ready[/green]")
            return True
        except pymysql.err.OperationalError:
            time.sleep(2)
    console.print(f"[red]✗ MySQL not ready after {max_wait}s[/red]")
    return False


def run_workshop_command(
    command: str,
    db_type: str,
    config: dict,
    scale: str = "tiny",
) -> bool:
    """Run a bad_data_workshop.py command."""
    cmd = [
        "uv", "run", "--script", "bad_data_workshop.py",
        command,
        "--db-type", db_type,
        "--host", config["host"],
        "--port", str(config["port"]),
        "--database", config["database"],
        "--user", config["user"],
        "--password", config["password"],
    ]
    if command == "setup":
        cmd.extend(["--scale", scale])

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        console.print(f"[red]Workshop {command} failed[/red]")
        console.print(result.stdout)
        console.print(result.stderr)
        return False
    console.print(result.stdout)
    return True


def verify_postgres_tables() -> tuple[bool, int]:
    """Verify tables were created in PostgreSQL."""
    import psycopg2

    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    # Count tables in schema
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'bad_data_workshop'
    """)
    table_count = cur.fetchone()[0]

    # Count total rows across all tables
    cur.execute("""
        SELECT SUM(n_live_tup)
        FROM pg_stat_user_tables
        WHERE schemaname = 'bad_data_workshop'
    """)
    row_count = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return table_count > 0, int(row_count)


def verify_postgres_empty() -> bool:
    """Verify PostgreSQL schema was removed."""
    import psycopg2

    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.schemata
        WHERE schema_name = 'bad_data_workshop'
    """)
    schema_exists = cur.fetchone()[0] > 0

    cur.close()
    conn.close()

    return not schema_exists


def verify_mysql_tables() -> tuple[bool, int]:
    """Verify tables were created in MySQL."""
    import pymysql

    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()

    # Count tables with our prefix
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'workshop'
        AND table_name LIKE 'bdw_%'
    """)
    table_count = cur.fetchone()[0]

    # Get row counts
    cur.execute("""
        SELECT SUM(table_rows)
        FROM information_schema.tables
        WHERE table_schema = 'workshop'
        AND table_name LIKE 'bdw_%'
    """)
    row_count = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return table_count > 0, int(row_count)


def verify_mysql_empty() -> bool:
    """Verify MySQL tables were removed."""
    import pymysql

    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'workshop'
        AND table_name LIKE 'bdw_%'
    """)
    table_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return table_count == 0


def test_database(
    db_type: Literal["postgres", "mysql"],
    config: dict,
    verify_tables_func,
    verify_empty_func,
) -> bool:
    """Run full test cycle for a database."""
    console.print(
        Panel(
            f"[bold cyan]Testing {db_type.upper()}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Setup
    console.print("\n[yellow]Step 1: Running setup...[/yellow]")
    if not run_workshop_command("setup", db_type, config, scale="tiny"):
        return False

    # Verify tables exist
    console.print("\n[yellow]Step 2: Verifying tables were created...[/yellow]")
    tables_exist, row_count = verify_tables_func()
    if not tables_exist:
        console.print("[red]✗ No tables found![/red]")
        return False
    console.print(f"[green]✓ Tables created with ~{row_count:,} rows[/green]")

    # Teardown
    console.print("\n[yellow]Step 3: Running teardown...[/yellow]")
    if not run_workshop_command("teardown", db_type, config):
        return False

    # Verify cleanup
    console.print("\n[yellow]Step 4: Verifying cleanup...[/yellow]")
    is_empty = verify_empty_func()
    if not is_empty:
        console.print("[red]✗ Tables still exist after teardown![/red]")
        return False
    console.print("[green]✓ All tables removed[/green]")

    console.print(
        Panel(
            f"[bold green]✓ {db_type.upper()} test passed![/bold green]",
            border_style="green",
        )
    )
    return True


def main() -> int:
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test Bad Data Workshop")
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Skip Docker start/stop (containers must be running)",
    )
    parser.add_argument(
        "--db",
        choices=["postgres", "mysql", "both"],
        default="both",
        help="Which database to test (default: both)",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold]Bad Data Workshop - Integration Test[/bold]\n\n"
            "This will test setup and teardown against local Docker databases.",
            border_style="blue",
        )
    )

    results = {}

    try:
        # Check Docker is running
        if not args.no_docker:
            if not check_docker_running():
                console.print(
                    Panel(
                        "[bold red]Docker daemon is not running![/bold red]\n\n"
                        "Please start Docker Desktop or the Docker daemon, then retry.\n\n"
                        "Alternatively, run with [cyan]--no-docker[/cyan] if containers "
                        "are already running.",
                        border_style="red",
                    )
                )
                return 1
            start_docker_containers()

        # Wait for databases
        if args.db in ("postgres", "both"):
            if not wait_for_postgres():
                return 1

        if args.db in ("mysql", "both"):
            if not wait_for_mysql():
                return 1

        # Run tests
        if args.db in ("postgres", "both"):
            results["postgres"] = test_database(
                "postgres",
                POSTGRES_CONFIG,
                verify_postgres_tables,
                verify_postgres_empty,
            )

        if args.db in ("mysql", "both"):
            results["mysql"] = test_database(
                "mysql",
                MYSQL_CONFIG,
                verify_mysql_tables,
                verify_mysql_empty,
            )

        # Summary
        console.print("\n")
        console.print(Panel("[bold]Test Summary[/bold]", border_style="blue"))
        all_passed = True
        for db, passed in results.items():
            status = "[green]PASSED[/green]" if passed else "[red]FAILED[/red]"
            console.print(f"  {db.upper()}: {status}")
            if not passed:
                all_passed = False

        return 0 if all_passed else 1

    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted[/yellow]")
        return 130

    finally:
        if not args.no_docker:
            stop_docker_containers()


if __name__ == "__main__":
    sys.exit(main())
