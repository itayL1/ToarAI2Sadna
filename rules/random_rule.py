import random

from compsoc.profile import Profile


def random_rule(profile: Profile, candidate: int) -> int:
    return random.randint(0, 1_000_000)
