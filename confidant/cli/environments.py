# confidant/cli/environments.py

import os
import shutil
import typer
import yaml
from confidant.core.utils import (
    load_meta,
    load_active_config,
    save_active_config,
)

from confidant.config import *

app = typer.Typer(help="Environment configuration commands for Confidant.")

@app.command()
def add_var(
    key: str = typer.Option(..., "--key", help="Key name to add."),
    value: str = typer.Option(..., "--value", help="Value to assign to the key."),
    env: str = typer.Option(None, "--env", help="Environment to add variable in (default: current)")
):
    """
    Add a new variable to active environment config.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")

    config = load_active_config(env)

    if key in config:
        typer.secho(f"Key '{key}' already exists. Use update-var to modify.", fg=typer.colors.RED)
        raise typer.Exit()

    config[key] = value
    save_active_config(env, config)

    typer.secho(f"✅ Added {key}={value} to '{env}' environment.", fg=typer.colors.GREEN)

@app.command()
def update_var(
    key: str = typer.Option(..., "--key", help="Key name to update."),
    value: str = typer.Option(..., "--value", help="New value to assign."),
    env: str = typer.Option(None, "--env", help="Environment to update variable in (default: current)")
):
    """
    Update an existing variable in active environment config.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")

    config = load_active_config(env)

    if key not in config:
        typer.secho(f"Key '{key}' does not exist. Use add-var to create it.", fg=typer.colors.RED)
        raise typer.Exit()

    config[key] = value
    save_active_config(env, config)

    typer.secho(f"✅ Updated {key} to {value} in '{env}' environment.", fg=typer.colors.GREEN)

@app.command()
def delete_var(
    key: str = typer.Option(..., "--key", help="Key name to delete."),
    env: str = typer.Option(None, "--env", help="Environment to delete variable from (default: current)")
):
    """
    Delete a variable from active environment config.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")

    config = load_active_config(env)

    if key not in config:
        typer.secho(f"Key '{key}' not found in environment '{env}'.", fg=typer.colors.RED)
        raise typer.Exit()

    del config[key]
    save_active_config(env, config)

    typer.secho(f"✅ Deleted {key} from '{env}' environment.", fg=typer.colors.GREEN)

@app.command()
def list_vars(env: str = typer.Option(None, "--env", help="Environment to list variables from (default: current)")):
    """
    List all variables in active environment config.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")

    config = load_active_config(env)

    typer.secho(f"📦 Config Variables in '{env}':", fg=typer.colors.BLUE)
    if not config:
        typer.echo("• No variables found.")
        return

    for k, v in config.items():
        typer.echo(f"  - {k} = {v}")

@app.command()
def show_env_config(env: str = typer.Option(None, "--env", help="Environment to inspect (default: current)")):
    """
    Show config details of an environment.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")
    
    env_path = os.path.join(CONFIDANT_DIR, env)
    config_path = os.path.join(env_path, "config.yaml")
    versions_path = os.path.join(env_path, "versions")

    if not os.path.exists(env_path):
        typer.secho(f"Environment '{env}' does not exist.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.secho(f"📦 Environment: {env}", fg=typer.colors.BLUE)
    typer.echo(f"• Active Config: {config_path}")
    if os.path.exists(versions_path):
        versions = os.listdir(versions_path)
        typer.echo(f"• Saved Versions: {', '.join(versions) if versions else 'None'}")
    else:
        typer.echo("• No saved versions yet.")

@app.command()
def promote_version(
    version_name: str = typer.Option(..., "--version-name", help="Name of the version to promote."),
    env: str = typer.Option(None, "--env", help="Environment to promote in (default: current)")
):
    """
    Promote a saved version to be the active config for an environment.
    """
    meta = load_meta()
    if not env:
        env = meta.get("current_env", "default")
    
    versions_dir = os.path.join(CONFIDANT_DIR, env, "versions", version_name)
    version_config_path = os.path.join(versions_dir, "config.yaml")
    active_config_path = os.path.join(CONFIDANT_DIR, env, "config.yaml")

    if not os.path.exists(version_config_path):
        typer.secho(f"Version '{version_name}' does not exist in environment '{env}'.", fg=typer.colors.RED)
        raise typer.Exit()

    shutil.copy(version_config_path, active_config_path)
    typer.secho(f"✅ Promoted version '{version_name}' to active config in '{env}'.", fg=typer.colors.GREEN)

@app.command()
def edit_env_config(env: str = typer.Option(..., "--env", help="Environment to edit (future support)")):
    """
    (Placeholder) Edit environment config metadata manually.
    """
    typer.secho(f"⚙️  Editing environment '{env}' manually is not yet supported (coming soon).", fg=typer.colors.YELLOW)
