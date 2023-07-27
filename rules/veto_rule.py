from compsoc.profile import Profile


def veto_rule(profile: Profile, candidate: int) -> int:
    veto_score = 0

    for frequency, ballot in profile.pairs:
        ballot_is_distorted = len(ballot) != len(profile.candidates)

        if ballot_is_distorted:
            candidate_is_last_in_ballot = candidate not in ballot
        else:
            candidate_is_last_in_ballot = ballot[-1] == candidate

        if candidate_is_last_in_ballot:
            veto_score += frequency

    return -veto_score
