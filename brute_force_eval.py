import itertools
import json
import math
from time import time
from typing import Collection, List

from compsoc.evaluate import get_rule_utility
from compsoc.profile import Profile
from tqdm import tqdm


def brute_force_eval(pairs: Collection[dict], topn: int):
    profile = _construct_profile(pairs)

    all_permutations = itertools.permutations(profile.candidates)
    best_top_permutation_score = -float('inf')
    best_top_permutation = None
    best_topn_permutation_score = -float('inf')
    best_topn_permutation = None
    for permutation in tqdm(all_permutations, total=math.factorial(len(profile.candidates))):
        rule_func = _build_dummy_rule_for_ranking(ranking=permutation)
        results = get_rule_utility(
            profile=profile,
            rule=rule_func,
            topn=topn
        )
        if results['top'] > best_top_permutation_score:
            best_top_permutation_score = results['top']
            best_top_permutation = permutation
        if results['topn'] > best_topn_permutation_score:
            best_topn_permutation_score = results['topn']
            best_topn_permutation = permutation

    _store_and_print_results(
        best_top_permutation, best_top_permutation_score, best_topn_permutation, best_topn_permutation_score
    )


def _construct_profile(pairs):
    pair_tuples = {
        (pair["frequency"], tuple(pair["ballot"]))
        for pair in pairs
    }
    profile = Profile(pairs=pair_tuples)
    return profile


def _store_and_print_results(
    best_top_permutation, best_top_permutation_score, best_topn_permutation, best_topn_permutation_score
):
    best_permutations_details = dict(
        best_top_permutation_score=best_top_permutation_score,
        best_top_permutation=best_top_permutation,
        best_topn_permutation_score=best_topn_permutation_score,
        best_topn_permutation=best_topn_permutation,
    )
    best_permutations_details_json = json.dumps(best_permutations_details, indent=4)
    print(f"best_permutations_details: {best_permutations_details_json}")
    with open(f'./results_{time()}.json', 'w') as f:
        f.write(best_permutations_details_json)


def _build_dummy_rule_for_ranking(ranking: List[int]):
    def dummy_rule(profile: Profile, candidate: int) -> int:
        candidate_score = -(ranking.index(candidate) + 1)
        return candidate_score

    return dummy_rule


if __name__ == '__main__':
    brute_force_eval(
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
