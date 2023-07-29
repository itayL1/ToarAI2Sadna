from compsoc.profile import Profile

BORDA_VETO_DISTORTION_RATIO_THRESHOLD = 0.8


def borda_veto_hybrid_rule(profile: Profile, candidate: int) -> int:
    # calculate the distortion ratio of the profile
    average_ballot_length = sum(len(ballot) for _, ballot in profile.pairs) / len(profile.pairs)
    profile_distortion_ratio = 1 - (average_ballot_length / len(profile.candidates))

    if profile_distortion_ratio >= BORDA_VETO_DISTORTION_RATIO_THRESHOLD:
        # veto rule:
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
    else:
        # borda rule
        top_score = len(profile.candidates) - 1
        scores = [
            frequency * (top_score - ballot.index(candidate))
            for frequency, ballot in profile.pairs
            if candidate in ballot
        ]
        return sum(scores)
