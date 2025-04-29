# confidant/cli/main.py
import typer
from confidant.cli import project , secrets , versions , info , environments

app = typer.Typer(help="Confidant CLI - Manage your secure settings and secrets easily.")

app.add_typer(project.app, name="project")
app.add_typer(secrets.app, name="secrets")
app.add_typer(versions.app, name="versions")
app.add_typer(info.app, name="info")
app.add_typer(environments.app, name="environments")
