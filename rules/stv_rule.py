import pyrankvote
from compsoc.profile import Profile
from pyrankvote import Candidate, Ballot


def stv_rule(profile: Profile, candidate: int) -> int:
    candidate_to_package_candidate = {
        c: Candidate(str(c)) for c in profile.candidates
    }

    package_ballots = [
        Ballot(ranked_candidates=[
            candidate_to_package_candidate[c]
            for c in ballot
        ])
        for frequency, ballot in profile.pairs
        for _ in range(frequency)
    ]
    election_result = pyrankvote.single_transferable_vote(
        list(candidate_to_package_candidate.values()),
        package_ballots,
        number_of_seats=(len(profile.candidates) - 1)
    )
    winners_orig_candidates = [
        int(package_c.name)
        for package_c in election_result.get_winners()
    ]
    num_candidates = len(profile.candidates)
    candidate_to_score = {
        c: num_candidates - i
        for i, c in enumerate(winners_orig_candidates)
    }
    final_score = candidate_to_score.get(candidate, 0)
    return final_score
