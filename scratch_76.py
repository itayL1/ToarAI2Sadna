from compsoc.evaluate import voter_subjective_utility_for_elected_candidate

utility_for_top, total_utility = voter_subjective_utility_for_elected_candidate(
    vote=['A', 'B', 'C', 'D', 'E'],
    elected=('C', 'A', 'E', 'B', 'D'),
    topn=3
)
print(dict(utility_for_top=utility_for_top, total_utility=total_utility))
