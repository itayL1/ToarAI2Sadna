from typing import Callable, Collection

from compsoc.evaluate import get_rule_utility
from compsoc.profile import Profile

from rules.borda_rule import borda_rule
from rules.chatGPTs_kemeny_rule import kemeny_rule
from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.k_approval_rule import k_approval_rule
from rules.maximin_rule import maximin_rule
from rules.plurality_rule import plurality_rule
from rules.simpson_rule import simpson_rule
from rules.veto_rule import veto_rule


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
            {"frequency": 3, "ballot": [4, 9, 8, 7, 6, 5, 3, 0, 2, 1]},
            {"frequency": 56, "ballot": [5, 0, 1, 2, 3, 4, 6, 9, 7, 8]},
            {"frequency": 2394, "ballot": [5, 0, 1, 2, 3, 4, 6, 7, 8, 9]},
            {"frequency": 1249, "ballot": [5, 0, 1, 2, 3, 4, 6, 8, 7, 9]},
            {"frequency": 2099, "ballot": [5, 0, 1, 2, 3, 4, 6, 7, 9, 8]},
            {"frequency": 2099, "ballot": [4, 9, 8, 7, 6, 5, 3, 2, 1, 0]},
            {"frequency": 3, "ballot": [5, 0, 1, 2, 3, 4, 6, 9, 8, 7]},
            {"frequency": 56, "ballot": [4, 9, 8, 7, 6, 5, 3, 1, 0, 2]},
            {"frequency": 1249, "ballot": [4, 9, 8, 7, 6, 5, 3, 2, 0, 1]},
            {"frequency": 396, "ballot": [4, 9, 8, 7, 6, 5, 3, 1, 2, 0]},
            {"frequency": 396, "ballot": [5, 0, 1, 2, 3, 4, 6, 8, 9, 7]},
        ],
        topn=1
    )
