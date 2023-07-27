from compsoc.profile import Profile

GAMMA = 0.1


def borda_gamma_rule(profile: Profile, candidate: int) -> int:
    scores = [
        frequency * (GAMMA ** ballot.index(candidate))
        for frequency, ballot in profile.pairs
        if candidate in ballot
    ]
    return sum(scores)
