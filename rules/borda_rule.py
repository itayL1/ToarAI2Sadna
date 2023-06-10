from compsoc.profile import Profile

GAMMA = 1


def borda_rule(profile: Profile, candidate: int) -> float:
    scores = [
        pair[0] * (GAMMA ** pair[1].index(candidate))
        for pair in profile.pairs
    ]
    return sum(scores)
