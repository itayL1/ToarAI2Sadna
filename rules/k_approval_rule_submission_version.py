from compsoc.profile import Profile

K = 9


def k_approval_rule(profile: Profile, candidate: int) -> int:
    candidate_scores = {c: 0 for c in profile.candidates}

    for frequency, ballot in profile.pairs:
        approved_candidates = ballot[:K]
        for approved_candidate in approved_candidates:
            candidate_scores[approved_candidate] += frequency

    return candidate_scores[candidate]
