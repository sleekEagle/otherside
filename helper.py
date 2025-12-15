from pathlib import Path
from typing import Any
import yaml
import os

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
    

def concat_summaries(dir):
    files = [file for file in os.listdir(dir) if file.endswith('.txt')]
    files.sort()
    concat = ''
    for i,file in enumerate(files):
        if file == 'all_summaries.txt':
            continue
        concat += f'\n\n=== Video {i+1} ===\n\n'
        file_path = os.path.join(dir, file)
        with open(file_path, 'r') as f:
            content = f.read()
            concat += content
    out_path = os.path.join(dir, 'all_summaries.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(concat)
    pass


# concat_summaries("summary")

