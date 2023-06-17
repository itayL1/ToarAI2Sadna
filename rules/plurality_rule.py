from compsoc.profile import Profile


def plurality_rule(profile: Profile, candidate: int) -> int:
    candidate_score = sum(
        frequency
        for frequency, ballot in profile.pairs
        if ballot[0] == candidate
    )
    return candidate_score
