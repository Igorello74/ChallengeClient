import json


def find_sum(d: dict) -> int:
    total = 0
    for value in d.values():
        if isinstance(value, dict):
            total += find_sum(value)
        else:
            total += int(value)
    return total


def solve(data: str) -> str:
    parsed = json.loads(data)
    return str(find_sum(parsed))
