import asyncio
import json
from pathlib import Path


_ROOT = Path(__file__).resolve().parent.parent.parent


def _data_dir() -> Path:
    d = _ROOT / "data" / "trees"
    d.mkdir(parents=True, exist_ok=True)
    return d


async def save_tree(tree_id: str, tree_data: dict) -> None:
    def _put():
        path = _data_dir() / f"{tree_id}.json"
        path.write_text(json.dumps(tree_data, indent=2))

    await asyncio.to_thread(_put)


async def load_tree(tree_id: str) -> dict | None:
    def _get():
        path = _data_dir() / f"{tree_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    return await asyncio.to_thread(_get)


async def list_trees() -> list[dict]:
    def _list():
        result = []
        for path in _data_dir().glob("*.json"):
            data = json.loads(path.read_text())
            result.append(data)
        return result

    return await asyncio.to_thread(_list)


async def delete_tree(tree_id: str) -> None:
    def _delete():
        path = _data_dir() / f"{tree_id}.json"
        if path.exists():
            path.unlink()

    await asyncio.to_thread(_delete)
