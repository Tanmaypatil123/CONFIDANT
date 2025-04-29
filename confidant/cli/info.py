# confidant/cli/info.py

import typer
import os
import yaml
from confidant.config import CONFIDANT_DIR, META_FILE

app = typer.Typer(help="Info and status commands for Confidant.")

VERSION = "0.1.0"  # CLI/SDK version (update during releases)

def load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            return yaml.safe_load(f)
    return {}

@app.command()
def version():
    """
    Show Confidant CLI and SDK version.
    """
    typer.secho(f"Confidant Version: {VERSION}", fg=typer.colors.GREEN)

@app.command()
def status():
    """
    Show current project status.
    """
    if not os.path.exists(CONFIDANT_DIR):
        typer.secho("Not a Confidant project (missing .confidant/ folder).", fg=typer.colors.RED)
        raise typer.Exit()

    meta = load_meta()
    typer.secho("📊 Confidant Project Status:", fg=typer.colors.BLUE)
    typer.echo(f"• Project Name: {meta.get('project_name', 'unknown')}")
    typer.echo(f"• Created At: {meta.get('created_at', 'unknown')}")
    typer.echo(f"• Current Environment: {meta.get('current_env', 'default')}")
    typer.echo(f"• Available Environments: {', '.join(meta.get('environments', []))}")
