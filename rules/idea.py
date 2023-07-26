from compsoc.profile import Profile

from rules.borda_gamma_rule import borda_gamma_rule
from rules.borda_rule import borda_rule
from rules.chatGPTs_kemeny_rule import kemeny_rule
from rules.copeland_rule import copeland_rule
from rules.k_approval_rule import k_approval_rule
from rules.plurality_rule import plurality_rule
from rules.veto_rule import veto_rule

KEMENY_RULE_MAX_SUPPORTED_CANDIDATES_COUNT = 7


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
        pairs_with_best_candidates = {
            (frequency, tuple(c for c in ballot if c in candidates_for_kemeny_rule))
            for frequency, ballot in profile.pairs
        }
        profile_with_best_candidates = Profile(
            pairs=pairs_with_best_candidates,
            num_candidates=KEMENY_RULE_MAX_SUPPORTED_CANDIDATES_COUNT,
            distorted=True
        )
        final_score = kemeny_rule(profile_with_best_candidates, candidate)

    print(dict(candiadte=candidate, final_score=final_score))
    return final_score

