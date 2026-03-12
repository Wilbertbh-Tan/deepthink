import json
from pathlib import Path

from .config import get_settings


def _trees_dir() -> Path:
    path = Path(get_settings().data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_tree(tree_id: str, tree_data: dict) -> None:
    file = _trees_dir() / f"{tree_id}.json"
    file.write_text(json.dumps(tree_data, indent=2))


def load_tree(tree_id: str) -> dict | None:
    file = _trees_dir() / f"{tree_id}.json"
    if not file.exists():
        return None
    return json.loads(file.read_text())


def list_trees() -> list[dict]:
    trees = []
    for file in _trees_dir().glob("*.json"):
        data = json.loads(file.read_text())
        trees.append(data)
    return trees


def delete_tree(tree_id: str) -> bool:
    file = _trees_dir() / f"{tree_id}.json"
    if file.exists():
        file.unlink()
        return True
    return False
