import math
from compsoc.profile import Profile

from rules.k_approval_rule import build_k_approval_rule


def build_k_approval_rule_percentage_version(k_percentage: float):
    def k_approval_rule_percentage_version(profile: Profile, candidate: int) -> int:
        k = max(math.ceil(len(profile.candidates) * (k_percentage / 100)), 2)
        final_rule = build_k_approval_rule(k)
        score = final_rule(profile, candidate)
        return score

    return k_approval_rule_percentage_version
