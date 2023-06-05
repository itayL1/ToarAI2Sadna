from typing import Callable

import requests
from compsoc.profile import Profile

from rules.example_rule import copeland_rule

SERVER_URL = "https://api.algocratic.org/execute_rule"


def eval_rule(rule_func: Callable[[Profile, int], int]):
    rule_file_content = _read_rule_file(rule_func)

    data = {
        "code": rule_file_content,
        "pairs": [
            {"frequency": 5, "ballot": [1, 2, 3]},
            {"frequency": 6, "ballot": [3, 2, 1]},
            {"frequency": 6, "ballot": [1, 3, 2]}
        ],
        "topn": 1,
        "timeout": 60
    }

    response = requests.post(SERVER_URL, json=data)
    response.raise_for_status()
    print(f"response: {response.json()}")


def _read_rule_file(rule_func: Callable[[Profile, int], int]) -> str:
    rule_file_path = rule_func.__code__.co_filename
    with open(rule_file_path, 'r') as f:
        rule_file_content = f.read()
    return rule_file_content


if __name__ == '__main__':
    eval_rule(rule_func=copeland_rule)
