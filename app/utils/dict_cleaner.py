from typing import Sequence

def remove_keys(keys: Sequence[str], data: dict, is_complaint=True):
    for key in keys:
        if key in data:
            data.pop(key)
    if is_complaint and data.get("category") == "другое":
        data.pop("category")
    return data