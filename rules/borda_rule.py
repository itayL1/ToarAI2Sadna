from compsoc.profile import Profile


def borda_rule(profile: Profile, candidate: int) -> int:
    top_score = len(profile.candidates) - 1
    scores = [
        frequency * (top_score - ballot.index(candidate))
        for frequency, ballot in profile.pairs
        if candidate in ballot
    ]
    return sum(scores)
