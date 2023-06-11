from collections import Counter
from compsoc.profile import Profile


def plurality_rule(profile: Profile, candidate: int) -> int:
    import json
    raise Exception(f"json.dumps(profile.pairs): {json.dumps(tuple(profile.pairs))}")

    ballots = [ballot[0] for frequency, ballot in profile.pairs for _ in range(frequency)]
    candidate_scores = Counter(ballots)

    return candidate_scores[candidate]
