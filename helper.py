from pathlib import Path
from typing import Any
import yaml

def read_yaml(path: str | Path) -> Any:
    """
    Read a YAML file and return the parsed Python object.
    Raises FileNotFoundError or yaml.YAMLError on error.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"YAML file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)