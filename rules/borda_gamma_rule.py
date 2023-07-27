from compsoc.profile import Profile


def build_borda_gamma_rule(gamma: float):
    def borda_gamma_rule(profile: Profile, candidate: int) -> int:
        scores = [
            frequency * (gamma ** ballot.index(candidate))
            for frequency, ballot in profile.pairs
            if candidate in ballot
        ]
        return sum(scores)

    return borda_gamma_rule
