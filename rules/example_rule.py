import numpy as np
from compsoc.profile import Profile


def copeland_rule(profile: Profile, candidate: int) -> int:
    scores = []
    for m in profile.candidates:
        preference = profile.get_net_preference(candidate, m)  # preference over m
        scores.append(np.sign(preference))  # win or not
    # Return the total score
    return sum(scores)
