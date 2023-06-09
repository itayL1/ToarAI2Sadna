from compsoc.profile import Profile


def maximin_rule(profile: Profile, candidate: int) -> int:
    possible_x_scores = []

    x = candidate
    for frequency, ballot in profile.pairs:
        for y in profile.candidates:
            if y != candidate:
                preference = profile.get_net_preference(x, y)
                n_x_gt_y = frequency if preference > 0 else 0
                possible_x_scores.append(n_x_gt_y)
    return min(possible_x_scores)
