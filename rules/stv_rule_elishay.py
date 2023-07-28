from compsoc.profile import Profile
import numpy as np
from scipy.sparse import csr_matrix
from rules.plurality_rule import plurality_rule

def stv_rule_elishay(profile: Profile, candidate: int) -> int:
    m = len(profile.candidates) - 1  # Number of rounds
    num_alternatives = len(profile.candidates)
    scores = np.zeros(num_alternatives, dtype=float)
    score = 1
    votes = np.zeros(num_alternatives, dtype=float)

    for round in range(m):

        # Calculate plurality scores
        for frequency, ballot in profile.pairs:
            votes[ballot[0]] += frequency

        # Find the alternative with the least votes
        min_votes = np.min(votes)
        min_vote_indices = np.where(votes == min_votes)[0]

        if len(min_vote_indices) == 1:
            # Only one alternative has the least votes, eliminate it
            eliminated_alternative = min_vote_indices[0]
        else:
            # Multiple alternatives have the least votes, use the plurality rule to break ties
            eliminated_alternative = np.random.choice(min_vote_indices)

        # Eliminate the alternative by setting its score to infinity
        votes[eliminated_alternative] = np.inf
        votes[votes != np.inf] = 0
        scores[eliminated_alternative] = score
        score = score + 1

    # Find the alternative left standing (winner)
    winner = np.where(votes != np.inf)[0][0]
    scores[winner] = score
    return scores[candidate]