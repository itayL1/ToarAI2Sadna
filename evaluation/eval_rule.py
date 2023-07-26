from typing import Callable, Optional

import pandas as pd
from compsoc.evaluate import get_rule_utility
from compsoc.profile import Profile
from compsoc.voter_model import generate_random_votes, generate_distorted_from_normal_profile
from tqdm import tqdm

from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.maximin_rule import maximin_rule
from rules.simpson_rule import simpson_rule
from rules.veto_rule import veto_rule
from utils.random_utils import set_global_random_seed


def eval_rule(
    rule_func: Callable[[Profile, int], int],
    topn: int,
    distortion_ratio: float,
    eval_iterations_count: int,
    random_seed: Optional[int] = None,
    print_results: bool = False,
    verbose: bool = False
):
    if random_seed is not None:
        set_global_random_seed(random_seed)

    iterations_results = []
    pbar_base_message = "eval iterations progress"
    with tqdm(total=eval_iterations_count, desc=pbar_base_message) as pbar:
        for i in range(eval_iterations_count):
            profile = _generate_eval_profile(distortion_ratio)
            iteration_results = get_rule_utility(
                profile=profile,
                rule=rule_func,
                topn=topn,
                verbose=verbose
            )
            pbar.update()
            pbar.set_description(f"{pbar_base_message} (last iteration results: {iteration_results})")
            iterations_results.append({'iter_index': i, **iteration_results})
    iterations_results_df = pd.DataFrame(iterations_results)

    if print_results:
        print(f"\n\n{_titled('all iteration results:')}\n\n{iterations_results_df.round(1)}"
              f"\n\n\n{_titled('iteration results stats:')}\n\n{iterations_results_df.describe().round(1)}")

    return iterations_results_df


def _generate_eval_profile(distortion_ratio: float) -> Profile:
    pair_tuples = generate_random_votes(number_voters=1_000, number_candidates=20)
    pair_tuples_set = set(pair_tuples)
    assert len(pair_tuples) == len(pair_tuples_set)
    profile = Profile(pairs=pair_tuples_set)
    distorted_profile = generate_distorted_from_normal_profile(profile, distortion_ratio)
    return distorted_profile


def _titled(text: str) -> str:
    return f"{text}\n{'-' * len(text)}"


if __name__ == '__main__':
    # real compilation scores:
    # ----------------------
    # * plurality_rule: ~4,680 - ~4,840
    # * borda_rule: ~4,727 - ~4801

    eval_rule(
        rule_func=veto_rule,
        topn=9, # not sure yet
        distortion_ratio=0.5, # not sure yet
        eval_iterations_count=10,
        random_seed=42,
        print_results=True,
        verbose=False
    )
