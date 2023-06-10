from compsoc.profile import Profile


def simpson_rule(profile: Profile, candidate: int) -> int:
    scores = [
        profile.get_net_preference(candidate, m) for m in
        profile.candidates - {candidate}
    ]
    return min(scores)
