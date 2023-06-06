from compsoc.profile import Profile


def runoff(profile: Profile, candidate: int) -> int:
    candidates = profile.candidates

    # first round
    counts = {}
    for pref in self.pref_schedule.prefs:
        highest = pref[0]
        if highest in counts:
            counts[highest] += 1
        else:
            counts[highest] = 1

    first_round_winners = []
    scores = list(counts.values())
    highest_votes = max(scores)
    while highest_votes in scores:
        scores.remove(highest_votes)
    second_highest_votes = max(scores)
    for candidate in counts:
        if counts[candidate] == highest_votes:
            first_round_winners.append(candidate)
    if len(first_round_winners) == 1:
        for candidate in counts:
            if counts[candidate] == second_highest_votes:
                first_round_winners.append(candidate)

    print('The numbers of votes for each candidate in the first round:', counts)
    print('The first round winners are', first_round_winners)

    # second round
    counts = {c: 0 for c in first_round_winners}
    for candidate in first_round_winners:
        for pref in self.pref_schedule.prefs:
            ranks = [pref.index(c) for c in first_round_winners]
            if pref.index(candidate) == min(ranks):
                counts[candidate] += 1

    print('The numbers of votes for each candidate in the second round:', counts)
    print('The winner(s) is(are)', find_winner(counts))


def find_winner(aggregated_result):
    max_point = 0
    for point in aggregated_result.values():
        if point > max_point:
            max_point = point

    winner = []  # winner can be many, so use a list here
    for candidate in aggregated_result.keys():
        if aggregated_result[candidate] == max_point:
            winner.append(candidate)

    return winner
