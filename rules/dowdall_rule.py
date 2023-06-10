from compsoc.profile import Profile


def dowdall_rule(profile: Profile, candidate: int) -> int:
    top_score = len(profile.candidates) - 1
    scores = [
        pair[0] * ((top_score - pair[1].index(candidate)) / (pair[1].index(candidate) + 1))
        for pair in profile.pairs
    ]
    return sum(scores)
