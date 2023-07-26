import itertools
import math
from functools import lru_cache

from compsoc.profile import Profile
from tqdm import tqdm

from rules.borda_gamma_rule import borda_gamma_rule
from rules.borda_rule import borda_rule
from rules.chatGPTs_kemeny_rule import kemeny_rule
from rules.copeland_rule import copeland_rule
from rules.k_approval_rule import k_approval_rule
from rules.plurality_rule import plurality_rule
from rules.veto_rule import veto_rule

KEMENY_RULE_MAX_SUPPORTED_CANDIDATES_COUNT = 9


def idea_rule(profile: Profile, candidate: int) -> int:
    candidate_to_heuristic_score = dict()
    for c in profile.candidates:
        candidate_to_heuristic_score[c] = borda_rule(profile, c)

    candidates_sorted_by_heuristic_score_asc = list(sorted(
        candidate_to_heuristic_score.keys(), key=lambda c_: candidate_to_heuristic_score[c_])
    )
    candidates_for_kemeny_rule = candidates_sorted_by_heuristic_score_asc[-KEMENY_RULE_MAX_SUPPORTED_CANDIDATES_COUNT:]
    candidates_excluded_from_kemeny_rule = [c for c in candidates_sorted_by_heuristic_score_asc if c not in candidates_for_kemeny_rule]

    if candidate in candidates_excluded_from_kemeny_rule:
        final_score = -(list(reversed(candidates_excluded_from_kemeny_rule)).index(candidate) + 1)
    else:
        candidate_to_score = _clac_kemeny_scores(tuple(profile.candidates), tuple(profile.pairs), tuple(candidates_for_kemeny_rule))
        # pairs_with_best_candidates = {
        #     (frequency, tuple(c for c in ballot if c in candidates_for_kemeny_rule))
        #     for frequency, ballot in profile.pairs
        # }
        # profile_with_best_candidates = Profile(
        #     pairs=pairs_with_best_candidates,
        #     num_candidates=KEMENY_RULE_MAX_SUPPORTED_CANDIDATES_COUNT,
        #     distorted=True
        # )
        final_score = candidate_to_score[candidate]

    print(dict(candiadte=candidate, final_score=final_score))
    return final_score


@lru_cache(maxsize=1)
def _clac_kemeny_scores(candidates, pairs, candidates_to_consider):
    num_candidates = len(candidates)
    all_permutations = itertools.permutations(candidates_to_consider)
    min_distance = float('inf')

    candidate_ranking = None
    # for permutation in all_permutations:
    for permutation in tqdm(all_permutations, total=math.factorial(len(candidates_to_consider)), desc="kemeny_rule main loop", leave=False):
        distance = 0
        for frequency, ballot in pairs:

            # Calculate the Kendall tau distance between ballot and permutation
            n = len(permutation)
            tau_distance = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (ballot[i] < ballot[j] and permutation[i] > permutation[j]) or (
                            ballot[i] > ballot[j] and permutation[i] < permutation[j]):
                        tau_distance += 1

            distance += tau_distance * frequency

        if distance < min_distance:
            min_distance = distance
            candidate_ranking = list(permutation)

    candidate_to_score = {
        c: num_candidates - i
        for i, c in enumerate(candidate_ranking)
    }
    return candidate_to_score
