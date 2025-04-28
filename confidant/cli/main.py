# confidant/cli/main.py

import typer
from confidant.core.secrets import encrypt_secret, decrypt_secret
from cryptography.fernet import Fernet

app = typer.Typer(help="Confidant CLI - Manage your secure settings and secrets easily.")

VERSION = "0.1.0"  # Update this when releasing new versions!

@app.command()
def version():
    """
    Show the Confidant CLI and SDK version.
    """
    typer.secho(f"Confidant CLI Version: {VERSION}", fg=typer.colors.GREEN)

@app.command()
def generate_key():
    """
    Generate a new Confidant master key.
    """
    key = Fernet.generate_key().decode()
    typer.secho("🗝️  CONFIDANT_MASTER_KEY:", fg=typer.colors.BLUE)
    typer.echo(key)

@app.command()
def encrypt(value: str):
    """
    Encrypt a plain secret value.
    """
    try:
        encrypted = encrypt_secret(value)
        typer.secho("🔒 Encrypted Secret:", fg=typer.colors.GREEN)
        typer.echo(encrypted)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def decrypt(value: str):
    """
    Decrypt an encrypted secret value.
    """
    try:
        decrypted = decrypt_secret(value)
        typer.secho("🔓 Decrypted Secret:", fg=typer.colors.GREEN)
        typer.echo(decrypted)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def bulk_encrypt(
    input_file: str = typer.Option(..., "--input", help="Path to input YAML or JSON file."),
    output_file: str = typer.Option(..., "--output", help="Path to save encrypted output file.")
):
    """
    Encrypt all plain secret values in a config file (YAML or JSON).
    """
    import yaml
    import json
    from confidant.secrets import encrypt_secret

    try:
        # Load input file
        if input_file.endswith(".yaml") or input_file.endswith(".yml"):
            with open(input_file, "r") as f:
                data = yaml.safe_load(f)
        elif input_file.endswith(".json"):
            with open(input_file, "r") as f:
                data = json.load(f)
        else:
            typer.secho("Unsupported file type. Only .yaml, .yml, .json allowed.", fg=typer.colors.RED)
            raise typer.Exit()

        # Encrypt all string values
        def recursive_encrypt(d):
            if isinstance(d, dict):
                return {k: recursive_encrypt(v) for k, v in d.items()}
            elif isinstance(d, str):
                return encrypt_secret(d)
            else:
                return d

        encrypted_data = recursive_encrypt(data)

        # Save output
        if output_file.endswith(".yaml") or output_file.endswith(".yml"):
            with open(output_file, "w") as f:
                yaml.safe_dump(encrypted_data, f)
        elif output_file.endswith(".json"):
            with open(output_file, "w") as f:
                json.dump(encrypted_data, f, indent=2)

        typer.secho(f"✅ Bulk encryption complete! Output saved to {output_file}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error during bulk encryption: {e}", fg=typer.colors.RED)


@app.command()
def bulk_decrypt(
    input_file: str = typer.Option(..., "--input", help="Path to encrypted YAML or JSON file."),
    output_file: str = typer.Option(..., "--output", help="Path to save decrypted output file.")
):
    """
    Decrypt all ENC(...) secret values in a config file (YAML or JSON).
    """
    import yaml
    import json
    from confidant.secrets import decrypt_secret

    try:
        # Load input file
        if input_file.endswith(".yaml") or input_file.endswith(".yml"):
            with open(input_file, "r") as f:
                data = yaml.safe_load(f)
        elif input_file.endswith(".json"):
            with open(input_file, "r") as f:
                data = json.load(f)
        else:
            typer.secho("Unsupported file type. Only .yaml, .yml, .json allowed.", fg=typer.colors.RED)
            raise typer.Exit()

        # Decrypt all string values
        def recursive_decrypt(d):
            if isinstance(d, dict):
                return {k: recursive_decrypt(v) for k, v in d.items()}
            elif isinstance(d, str) and d.startswith("ENC(") and d.endswith(")"):
                return decrypt_secret(d)
            else:
                return d

        decrypted_data = recursive_decrypt(data)

        # Save output
        if output_file.endswith(".yaml") or output_file.endswith(".yml"):
            with open(output_file, "w") as f:
                yaml.safe_dump(decrypted_data, f)
        elif output_file.endswith(".json"):
            with open(output_file, "w") as f:
                json.dump(decrypted_data, f, indent=2)

        typer.secho(f"✅ Bulk decryption complete! Output saved to {output_file}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error during bulk decryption: {e}", fg=typer.colors.RED)

@app.command()
def validate_settings(
    input_file: str = typer.Option(..., "--input", help="Path to config YAML or JSON file to validate."),
):
    """
    Validate a settings config file against Pydantic rules.
    """
    import yaml
    import json
    from pydantic import BaseModel, ValidationError

    try:
        # Load input file
        if input_file.endswith(".yaml") or input_file.endswith(".yml"):
            with open(input_file, "r") as f:
                data = yaml.safe_load(f)
        elif input_file.endswith(".json"):
            with open(input_file, "r") as f:
                data = json.load(f)
        else:
            typer.secho("Unsupported file type. Only .yaml, .yml, .json allowed.", fg=typer.colors.RED)
            raise typer.Exit()

        # Create a simple dynamic model
        class DynamicSettings(BaseModel):
            __annotations__ = {k: type(v) for k, v in data.items()}

        # Validate by instantiating the model
        DynamicSettings(**data)

        typer.secho(f"✅ Validation Successful! {input_file} is valid.", fg=typer.colors.GREEN)

    except ValidationError as ve:
        typer.secho(f"❌ Validation Failed:\n{ve}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error during validation: {e}", fg=typer.colors.RED)


@app.command()
def migrate_key(
    old_key: str = typer.Option(..., "--old-key", help="Old CONFIDANT_MASTER_KEY used for encryption."),
    new_key: str = typer.Option(..., "--new-key", help="New CONFIDANT_MASTER_KEY for re-encryption."),
    input_file: str = typer.Option(..., "--input", help="Path to input encrypted YAML or JSON file."),
    output_file: str = typer.Option(..., "--output", help="Path to save newly encrypted output file.")
):
    """
    Migrate secrets from old master key to new master key.
    """
    import yaml
    import json
    from cryptography.fernet import Fernet

    try:
        # Load input file
        if input_file.endswith(".yaml") or input_file.endswith(".yml"):
            with open(input_file, "r") as f:
                data = yaml.safe_load(f)
        elif input_file.endswith(".json"):
            with open(input_file, "r") as f:
                data = json.load(f)
        else:
            typer.secho("Unsupported file type. Only .yaml, .yml, .json allowed.", fg=typer.colors.RED)
            raise typer.Exit()

        old_fernet = Fernet(old_key.encode())
        new_fernet = Fernet(new_key.encode())

        # Migrate encryption
        def recursive_migrate(d):
            if isinstance(d, dict):
                return {k: recursive_migrate(v) for k, v in d.items()}
            elif isinstance(d, str) and d.startswith("ENC(") and d.endswith(")"):
                # Decrypt with old key
                encrypted_part = d[4:-1]
                decrypted = old_fernet.decrypt(encrypted_part.encode()).decode()
                # Encrypt with new key
                re_encrypted = new_fernet.encrypt(decrypted.encode()).decode()
                return f"ENC({re_encrypted})"
            else:
                return d

        migrated_data = recursive_migrate(data)

        # Save output
        if output_file.endswith(".yaml") or output_file.endswith(".yml"):
            with open(output_file, "w") as f:
                yaml.safe_dump(migrated_data, f)
        elif output_file.endswith(".json"):
            with open(output_file, "w") as f:
                json.dump(migrated_data, f, indent=2)

        typer.secho(f"✅ Key migration complete! New file saved to {output_file}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error during key migration: {e}", fg=typer.colors.RED)
