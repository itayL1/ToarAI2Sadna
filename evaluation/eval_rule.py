from typing import Callable, Collection

from compsoc.evaluate import get_rule_utility
from compsoc.profile import Profile

from rules.chatGPTs_kemeny_rule import kemeny_rule
from rules.example_rule import copeland_rule


def eval_rule(rule_func: Callable[[Profile, int], int], pairs: Collection[dict], topn: int):
    pair_tuples = {
        (pair["frequency"], tuple(pair["ballot"]))
        for pair in pairs
    }
    results = get_rule_utility(
        profile=Profile(pairs=pair_tuples),
        rule=rule_func,
        topn=topn
    )
    print(f"results: {results}")


if __name__ == '__main__':
    eval_rule(
        rule_func=kemeny_rule,
        pairs=[
            {"frequency": 5, "ballot": [1, 2, 3]},
            {"frequency": 6, "ballot": [3, 2, 1]},
            {"frequency": 6, "ballot": [1, 3, 2]}
        ],
        topn=1
    )
