from contextlib import contextmanager
from typing import Callable, Optional, Literal, Any

import pandas as pd
from compsoc.evaluate import get_rule_utility
from compsoc.profile import Profile
from compsoc.voter_model import generate_random_votes, generate_distorted_from_normal_profile, get_profile_from_model
from tqdm import tqdm

from rules.borda_veto_hybrid_rule import borda_veto_hybrid_rule
from rules.random_rule import random_rule
from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.k_approval_rule_submission_version import k_approval_rule
from rules.maximin_rule import maximin_rule
from rules.simpson_rule import simpson_rule
from rules.stv_rule import stv_rule
from rules.stv_rule_elishay import stv_rule_elishay
from rules.veto_rule import veto_rule
from utils.random_utils import set_global_random_seed

voter_model_names = Literal['random'] | Literal['gaussian'] | Literal['multinomial_dirichlet']


def eval_rule(
    rule_func: Callable[[Profile, int], int],
    topn: int,
    voters_model: voter_model_names,
    number_voters: int,
    number_candidates: int,
    distortion_ratio: float,
    eval_iterations_count: int,
    random_seed: Optional[int] = None,
    print_results: bool = False,
    show_progress_bar: bool = False,
    verbose: bool = False
):
    if random_seed is not None:
        set_global_random_seed(random_seed)

    iterations_results = []
    pbar_base_message = "eval iterations progress"
    with _open_progress_bar_if_needed(show_progress_bar, total=eval_iterations_count, desc=pbar_base_message) as pbar:
        for i in range(eval_iterations_count):
            profile = generate_eval_profile(
                voters_model, number_voters, number_candidates, distortion_ratio
            )
            iteration_results = get_rule_utility(
                profile=profile,
                rule=rule_func,
                topn=topn,
                verbose=verbose
            )
            iterations_results.append({'eval_iter_index': i, 'score': iteration_results['topn']})
            if pbar:
                pbar.update()
                pbar.set_description(f"{pbar_base_message} (last iteration results: {iteration_results})")
    iterations_results_df = pd.DataFrame(iterations_results)

    if print_results:
        print(f"\n\n{_titled('all iteration results:')}\n\n{iterations_results_df.round(1)}"
              f"\n\n\n{_titled('iteration results stats:')}\n\n{iterations_results_df.describe().round(1)}")

    return iterations_results_df


def generate_eval_profile(
    voters_model: voter_model_names, number_voters: int, number_candidates: int, distortion_ratio: float
) -> Profile:
    # multinomial_dirichlet has a bug that happens in some probability
    allowed_retries_count = 2 if voters_model == 'multinomial_dirichlet' else 0
    profile = _call_with_retries(
        lambda: get_profile_from_model(number_candidates, number_voters, voters_model=voters_model, verbose=False),
        allowed_retries_count
    )

    distorted_profile = generate_distorted_from_normal_profile(profile, distortion_ratio)
    return distorted_profile


def _call_with_retries(func: Callable[[], Any], allowed_retries_count: int) -> Any:
    executions_count = 0
    while True:
        executions_count += 1
        try:
            return func()
        except:
            if executions_count >= allowed_retries_count + 1:
                raise


@contextmanager
def _open_progress_bar_if_needed(open_progress_bar: bool, **pbar_params):
    if open_progress_bar:
        with tqdm(**pbar_params) as pbar:
            yield pbar
    else:
        yield None


def _titled(text: str) -> str:
    return f"{text}\n{'-' * len(text)}"


if __name__ == '__main__':
    # real compilation scores:
    # ----------------------
    # * plurality_rule: ~4,680 - ~4,840
    # * borda_rule: ~4,727 - ~4801

    eval_rule(
        rule_func=borda_veto_hybrid_rule,
        topn=9, # not sure yet
        voters_model='random',
        number_voters=1_000,
        number_candidates=20,
        distortion_ratio=0.5, # not sure yet
        eval_iterations_count=20,
        random_seed=42,
        print_results=True,
        show_progress_bar=True,
        verbose=False
    )
