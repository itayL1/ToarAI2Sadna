from collections import Counter
from compsoc.profile import Profile


def plurality_rule(profile: Profile, candidate: int) -> int:
    """
    Calculates the Plurality score for a candidate based on a profile.

    :param profile: The voting profile.
    :type profile: Profile
    :param candidate: The candidate for scoring.
    :type candidate: int
    :return: The Plurality score for the candidate.
    :rtype: int
    """
    ballots = [ballot[0] for frequency, ballot in profile.pairs for _ in range(frequency)]
    candidate_scores = Counter(ballots)

    return candidate_scores[candidate]
