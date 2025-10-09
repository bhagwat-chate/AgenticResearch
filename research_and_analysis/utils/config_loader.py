import os
import yaml
from pathlib import Path

def _product_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str | None = None) -> dict:
    """Load configuration YAML from a provided path or default location."""
    env_path = os.getenv("CONFIG_PATH")

    if config_path is None:
        config_path = env_path or str(_product_root() / "config" / "configuration.yaml")

    path = Path(config_path)

    if not path.is_absolute():
        path = _product_root() / path

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
