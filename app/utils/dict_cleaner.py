from typing import Sequence

def remove_keys(keys: Sequence[str], data: dict):
    for key in keys:
        if key in data:
            data.pop(key)
    return data