# confidant/cli/versions.py

import os
import shutil
import typer
import yaml
from confidant.core.utils import load_meta, save_meta
from confidant.config import CONFIDANT_DIR, META_FILE

app = typer.Typer(help="Version management commands for Confidant.")

@app.command()
def create_version(
    input_file: str = typer.Option(..., "--input", help="Path to current active config file."),
    version_name: str = typer.Option(..., "--version-name", help="Name of the version to save.")
):
    """
    Create/save a version inside the active environment.
    """
    meta = load_meta()
    current_env = meta.get("current_env", "default")
    versions_dir = os.path.join(CONFIDANT_DIR, current_env, "versions", version_name)
    os.makedirs(versions_dir, exist_ok=True)

    if not os.path.exists(input_file):
        typer.secho(f"Input file '{input_file}' does not exist.", fg=typer.colors.RED)
        raise typer.Exit()

    shutil.copy(input_file, os.path.join(versions_dir, "config.yaml"))

    typer.secho(f"✅ Version '{version_name}' created inside environment '{current_env}'.", fg=typer.colors.GREEN)

@app.command()
def switch_version(
    version_name: str = typer.Option(..., "--version-name", help="Name of the version to switch to.")
):
    """
    Switch to a saved version inside the active environment.
    """
    meta = load_meta()
    current_env = meta.get("current_env", "default")
    version_path = os.path.join(CONFIDANT_DIR, current_env, "versions", version_name, "config.yaml")
    active_config_path = os.path.join(CONFIDANT_DIR, current_env, "config.yaml")

    if not os.path.exists(version_path):
        typer.secho(f"Version '{version_name}' does not exist inside '{current_env}'.", fg=typer.colors.RED)
        raise typer.Exit()

    shutil.copy(version_path, active_config_path)

    typer.secho(f"✅ Switched to version '{version_name}' in environment '{current_env}'.", fg=typer.colors.GREEN)

@app.command()
def list_versions():
    """
    List all saved versions for the current environment.
    """
    meta = load_meta()
    current_env = meta.get("current_env", "default")
    versions_dir = os.path.join(CONFIDANT_DIR, current_env, "versions")

    if not os.path.exists(versions_dir):
        typer.secho("No versions found.", fg=typer.colors.RED)
        raise typer.Exit()

    versions = os.listdir(versions_dir)
    if not versions:
        typer.secho("No versions saved yet.", fg=typer.colors.YELLOW)
        return

    typer.secho(f"Available versions in '{current_env}':", fg=typer.colors.BLUE)
    for v in versions:
        typer.echo(f"  - {v}")

@app.command()
def delete_version(
    version_name: str = typer.Option(..., "--version-name", help="Name of the version to delete.")
):
    """
    Delete a saved version.
    """
    meta = load_meta()
    current_env = meta.get("current_env", "default")
    version_dir = os.path.join(CONFIDANT_DIR, current_env, "versions", version_name)

    if not os.path.exists(version_dir):
        typer.secho(f"Version '{version_name}' does not exist.", fg=typer.colors.RED)
        raise typer.Exit()

    shutil.rmtree(version_dir)
    typer.secho(f"✅ Version '{version_name}' deleted from environment '{current_env}'.", fg=typer.colors.GREEN)
