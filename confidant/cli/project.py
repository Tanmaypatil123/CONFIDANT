# confidant/cli/project.py

import os
import shutil
import yaml
import typer
from datetime import datetime
from confidant.config import CONFIDANT_DIR, META_FILE
from confidant.core.utils import save_meta , load_meta

app = typer.Typer(help="Project commands for Confidant (init, environments, etc.)")

@app.command()
def init(project_name: str = typer.Option("myproject", help="Project name for Confidant.")):
    """
    Initialize a new Confidant project.
    """
    try:
        os.makedirs(CONFIDANT_DIR, exist_ok=True)

        # Create default environment
        default_env_path = os.path.join(CONFIDANT_DIR, "default")
        os.makedirs(os.path.join(default_env_path, "versions"), exist_ok=True)
        with open(os.path.join(default_env_path, "config.yaml"), "w") as f:
            f.write("# Default environment config\n")

        # Create meta.yaml
        meta = {
            "project_name": project_name,
            "created_at": datetime.utcnow().isoformat(),
            "current_env": "default",
            "environments": ["default"]
        }
        save_meta(meta)

        typer.secho(f"✅ Confidant project '{project_name}' initialized successfully!", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error initializing project: {e}", fg=typer.colors.RED)

@app.command()
def create_env(name: str = typer.Option(..., help="Name of the environment to create.")):
    """
    Create a new environment.
    """
    try:
        env_path = os.path.join(CONFIDANT_DIR, name)
        if os.path.exists(env_path):
            typer.secho(f"Environment '{name}' already exists.", fg=typer.colors.RED)
            raise typer.Exit()

        os.makedirs(os.path.join(env_path, "versions"), exist_ok=True)
        with open(os.path.join(env_path, "config.yaml"), "w") as f:
            f.write(f"# Config for {name} environment\n")

        meta = load_meta()
        meta["environments"].append(name)
        save_meta(meta)

        typer.secho(f"✅ Environment '{name}' created successfully!", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error creating environment: {e}", fg=typer.colors.RED)

@app.command()
def use_env(name: str = typer.Option(..., help="Name of the environment to switch to.")):
    """
    Switch active environment.
    """
    try:
        meta = load_meta()
        if name not in meta.get("environments", []):
            typer.secho(f"Environment '{name}' does not exist.", fg=typer.colors.RED)
            raise typer.Exit()

        meta["current_env"] = name
        save_meta(meta)

        typer.secho(f"✅ Now using environment '{name}'.", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error switching environment: {e}", fg=typer.colors.RED)

@app.command()
def list_envs():
    """
    List all available environments.
    """
    try:
        meta = load_meta()
        envs = meta.get("environments", [])
        typer.secho("Available environments:", fg=typer.colors.BLUE)
        for env in envs:
            typer.echo(f"  - {env}")
    except Exception as e:
        typer.secho(f"Error listing environments: {e}", fg=typer.colors.RED)

@app.command()
def delete_env(name: str = typer.Option(..., help="Name of the environment to delete.")):
    """
    Delete an environment.
    """
    try:
        if name == "default":
            typer.secho("Cannot delete the default environment.", fg=typer.colors.RED)
            raise typer.Exit()

        env_path = os.path.join(CONFIDANT_DIR, name)
        if not os.path.exists(env_path):
            typer.secho(f"Environment '{name}' does not exist.", fg=typer.colors.RED)
            raise typer.Exit()

        shutil.rmtree(env_path)

        meta = load_meta()
        meta["environments"] = [env for env in meta["environments"] if env != name]
        save_meta(meta)

        typer.secho(f"✅ Environment '{name}' deleted successfully.", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error deleting environment: {e}", fg=typer.colors.RED)
