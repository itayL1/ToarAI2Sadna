import itertools
import math
from functools import lru_cache

from compsoc.profile import Profile
from tqdm import tqdm


def kemeny_rule(profile: Profile, candidate: int) -> int:
    candidates = tuple(profile.candidates)
    pairs = tuple(profile.pairs)

    candidate_to_score = _clac_kemeny_scores(candidates, pairs)

    candidate_score = candidate_to_score[candidate]
    return candidate_score


@lru_cache(maxsize=1)
def _clac_kemeny_scores(candidates, pairs):
    num_candidates = len(candidates)
    all_permutations = itertools.permutations(candidates)
    min_distance = float('inf')

    candidate_ranking = None
    # for permutation in all_permutations:
    for permutation in tqdm(all_permutations, total=math.factorial(num_candidates), desc="kemeny_rule main loop"):
        distance = 0
        for frequency, ballot in pairs:
            # filled_ballot = tuple(list(ballot) + [c for c in permutation if c not in ballot])
            filled_ballot = ballot

            # Calculate the Kendall tau distance between ballot and permutation
            n = len(filled_ballot)
            tau_distance = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (filled_ballot[i] < filled_ballot[j] and permutation[i] > permutation[j]) or (
                            filled_ballot[i] > filled_ballot[j] and permutation[i] < permutation[j]):
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
