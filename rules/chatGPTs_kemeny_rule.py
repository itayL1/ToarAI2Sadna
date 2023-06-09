import itertools
from compsoc.profile import Profile


def kemeny_rule(profile: Profile, candidate: int) -> int:
    """
    Calculates the Kemeny score for a candidate based on a profile.

    :param profile: The voting profile.
    :type profile: Profile
    :param candidate: The base candidate for scoring.
    :type candidate: int
    :return: The Kemeny score for the candidate.
    :rtype: int
    """
    candidates = profile.candidates
    num_candidates = len(candidates)
    all_permutations = itertools.permutations(candidates)

    min_distance = float('inf')
    candidate_ranking = None

    for permutation in all_permutations:
        distance = 0
        for frequency, ballot in profile.pairs:

            # Calculate the Kendall tau distance between ballot and permutation
            n = len(ballot)
            tau_distance = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (ballot[i] < ballot[j] and permutation[i] > permutation[j]) or (
                            ballot[i] > ballot[j] and permutation[i] < permutation[j]):
                        tau_distance += 1

            distance += tau_distance * frequency

        if distance < min_distance:
            min_distance = distance
            candidate_ranking = list(permutation)

    candidate_score = num_candidates - candidate_ranking.index(candidate)
    return candidate_score
