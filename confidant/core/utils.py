import os
import yaml
import json
from typing import Dict, Any, Optional, Tuple
from dotenv import dotenv_values

from confidant.config import (
    CONFIDANT_DIR, META_FILE
)



def load_meta() -> Dict[str, Any]:
    """
    Load metadata from .confidant/meta.yaml
    """
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_meta(meta: Dict[str, Any]):
    """
    Save metadata to .confidant/meta.yaml
    """
    os.makedirs(CONFIDANT_DIR, exist_ok=True)
    with open(META_FILE, "w") as f:
        yaml.safe_dump(meta, f)


def get_current_env(meta: Optional[Dict[str, Any]] = None) -> str:
    """
    Get the current active environment from meta.yaml
    """
    meta = meta or load_meta()
    return meta.get("current_env", "default")


def load_config(env: str) -> Dict[str, Any]:
    """
    Load config.yaml for the specified environment
    """
    path = os.path.join(CONFIDANT_DIR, env, "config.yaml")
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(env: str, data: Dict[str, Any]):
    """
    Save config.yaml for the specified environment
    """
    path = os.path.join(CONFIDANT_DIR, env, "config.yaml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(data, f)


def read_file(path: str) -> Tuple[Dict[str, Any], str]:
    """
    Read a YAML, JSON or .env file and return (data, filetype)
    """
    if path.endswith((".yaml", ".yml")):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}, "yaml"
    elif path.endswith(".json"):
        with open(path, "r") as f:
            return json.load(f), "json"
    elif path.endswith(".env"):
        return dotenv_values(path), "env"
    else:
        raise ValueError("Unsupported file type. Use .yaml, .json, or .env.")


def write_file(path: str, data: Dict[str, Any], filetype: str):
    """
    Write data back to YAML, JSON, or .env file
    """
    if filetype == "yaml":
        with open(path, "w") as f:
            yaml.safe_dump(data, f)
    elif filetype == "json":
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    elif filetype == "env":
        with open(path, "w") as f:
            for k, v in data.items():
                f.write(f"{k}={v}\n")
    else:
        raise ValueError(f"Unsupported file type for writing: {filetype}")
