
# confidant/cli/secrets.py

import typer
import os
import yaml
import json
from cryptography.fernet import Fernet
from dotenv import dotenv_values
from confidant.core.secrets import encrypt_secret, decrypt_secret
from confidant.core.utils import write_file , read_file

app = typer.Typer(help="Secrets management commands for Confidant.")



@app.command()
def generate_key():
    key = Fernet.generate_key().decode()
    typer.secho("🗝️  CONFIDANT_MASTER_KEY:", fg=typer.colors.BLUE)
    typer.echo(key)

@app.command()
def encrypt(value: str):
    try:
        encrypted = encrypt_secret(value)
        typer.secho("🔒 Encrypted Secret:", fg=typer.colors.GREEN)
        typer.echo(encrypted)
    except Exception as e:
        typer.secho(f"Error encrypting value: {e}", fg=typer.colors.RED)

@app.command()
def decrypt(value: str):
    try:
        decrypted = decrypt_secret(value)
        typer.secho("🔓 Decrypted Secret:", fg=typer.colors.GREEN)
        typer.echo(decrypted)
    except Exception as e:
        typer.secho(f"Error decrypting value: {e}", fg=typer.colors.RED)

@app.command()
def bulk_encrypt(input_file: str = typer.Option(..., "--input"), output_file: str = typer.Option(..., "--output")):
    try:
        data, file_type = read_file(input_file)
        def recursive_encrypt(d):
            if isinstance(d, dict):
                return {k: recursive_encrypt(v) for k, v in d.items()}
            elif isinstance(d, str):
                return encrypt_secret(d)
            else:
                return d
        encrypted_data = recursive_encrypt(data)
        write_file(output_file, encrypted_data, file_type)
        typer.secho(f"✅ Bulk encryption complete. Saved to {output_file}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error during bulk encryption: {e}", fg=typer.colors.RED)

@app.command()
def bulk_decrypt(input_file: str = typer.Option(..., "--input"), output_file: str = typer.Option(..., "--output")):
    try:
        data, file_type = read_file(input_file)
        def recursive_decrypt(d):
            if isinstance(d, dict):
                return {k: recursive_decrypt(v) for k, v in d.items()}
            elif isinstance(d, str) and d.startswith("ENC(") and d.endswith(")"):
                return decrypt_secret(d)
            else:
                return d
        decrypted_data = recursive_decrypt(data)
        write_file(output_file, decrypted_data, file_type)
        typer.secho(f"✅ Bulk decryption complete. Saved to {output_file}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error during bulk decryption: {e}", fg=typer.colors.RED)

@app.command()
def migrate_key(
    old_key: str = typer.Option(..., "--old-key"),
    new_key: str = typer.Option(..., "--new-key"),
    input_file: str = typer.Option(..., "--input"),
    output_file: str = typer.Option(..., "--output")
):
    try:
        data, file_type = read_file(input_file)
        old_fernet = Fernet(old_key.encode())
        new_fernet = Fernet(new_key.encode())

        def recursive_migrate(d):
            if isinstance(d, dict):
                return {k: recursive_migrate(v) for k, v in d.items()}
            elif isinstance(d, str) and d.startswith("ENC(") and d.endswith(")"):
                decrypted = old_fernet.decrypt(d[4:-1].encode()).decode()
                re_encrypted = new_fernet.encrypt(decrypted.encode()).decode()
                return f"ENC({re_encrypted})"
            else:
                return d

        migrated_data = recursive_migrate(data)
        write_file(output_file, migrated_data, file_type)
        typer.secho(f"✅ Key migration complete. Saved to {output_file}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error during key migration: {e}", fg=typer.colors.RED)
