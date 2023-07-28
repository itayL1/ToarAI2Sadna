import json
from pathlib import Path
from typing import Collection, Union, Literal, Optional, Set, List
from uuid import uuid4

import dask
import math
import pandas as pd
from dask.diagnostics import ProgressBar

from evaluation.eval_rule import eval_rule
from rules.borda_gamma_rule import build_borda_gamma_rule
from rules.borda_rule import borda_rule
from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.k_approval_rule import build_k_approval_rule
from rules.maximin_rule import maximin_rule
from rules.plurality_rule import plurality_rule
from rules.random_rule import random_rule
from rules.simpson_rule import simpson_rule
from rules.veto_rule import veto_rule


RULE_NAME_TO_FUNC = {
    'borda': borda_rule,
    'copeland': copeland_rule,
    'dowdall': dowdall_rule,
    'maximin': maximin_rule,
    'plurality': plurality_rule,
    'simpson': simpson_rule,
    'veto': veto_rule,
    'random': random_rule,
    **{
        f'borda_gamma_{gamma}': build_borda_gamma_rule(gamma)
        for gamma in (0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.25)
    },
    **{
        f'k_approval_k_{k}': build_k_approval_rule(k)
        for k in (2, 3, 4, 9)
    },
}


def run_experiment(
    rules: Union[Literal['all'], Set[str]],
    voter_models: Collection[str],
    top_n_percs: Collection[float],
    numbers_voters: Collection[int],
    numbers_candidates: Collection[int],
    distortion_ratios: Collection[float],
    eval_iterations_per_rule: int,
    random_seed: Optional[int] = None
):
    experiment_id = uuid4().hex
    print(f"experiment_id: '{experiment_id}'")

    if rules == 'all':
        rules = set(RULE_NAME_TO_FUNC.keys())
    elif not isinstance(rules, set):
        raise ValueError(f"unexpected rules param type: {type(rules)}")

    trails_params = [
        dict(
            voters_model=voter_model,
            number_voters=number_voters,
            number_candidates=number_candidates,
            distortion_ratio=distortion_ratio,
            topn_perc=topn_perc,
            topn_actual=math.ceil(number_candidates * (topn_perc / 100)),
            rule_name=rule_name
        )
        for rule_name in rules
        for voter_model in voter_models
        for topn_perc in top_n_percs
        for number_voters in numbers_voters
        for number_candidates in numbers_candidates
        for distortion_ratio in distortion_ratios
    ]
    trails_params = [tp for tp in trails_params if tp['topn_actual'] > 0]
    trails_results = _run_trails_in_parallel(trails_params, eval_iterations_per_rule, random_seed)

    _store_experiment_results(experiment_id, trails_results, experiment_extra_details=dict(
        eval_iterations_per_rule=eval_iterations_per_rule, random_seed=random_seed
    ))


def _run_trails_in_parallel(trails_params: List[dict], eval_iterations_per_rule: int, random_seed: Optional[int]) -> Collection[dict]:
    print(f"starting to run requested trails in parallel. total number of trails: {len(trails_params)}.")
    ProgressBar().register()

    delayed_results = []
    for trail_params in trails_params:
        trail_task = dask.delayed(_run_trail_task)(
            trail_params=trail_params, eval_iterations_per_rule=eval_iterations_per_rule, random_seed=random_seed
        )
        delayed_results.append(trail_task)

    trails_results = dask.compute(*delayed_results)
    return trails_results


def _run_trail_task(trail_params: dict, eval_iterations_per_rule: int, random_seed: Optional[int]) -> dict:
    rule_name = trail_params['rule_name']
    voters_model = trail_params['voters_model']
    topn = trail_params['topn_actual']
    number_candidates = trail_params['number_candidates']
    number_voters = trail_params['number_voters']
    distortion_ratio = trail_params['distortion_ratio']

    assert rule_name in RULE_NAME_TO_FUNC, f"unknown rule: '{rule_name}'"
    rule_func = RULE_NAME_TO_FUNC[rule_name]

    trail_results_df = eval_rule(
        rule_func=rule_func,
        topn=topn,
        voters_model=voters_model,
        number_voters=number_voters,
        number_candidates=number_candidates,
        distortion_ratio=distortion_ratio,
        eval_iterations_count=eval_iterations_per_rule,
        random_seed=random_seed,
        print_results=False,
        verbose=False
    )

    ret = dict(trail_params=trail_params, trail_results_df=trail_results_df)
    return ret


def _store_experiment_results(experiment_id: str, trails_results: Collection[dict], experiment_extra_details: dict):
    all_trails_dfs = []
    for trail_results in trails_results:
        trail_params = trail_results['trail_params']
        trail_results_df = trail_results['trail_results_df']
        trail_params_and_results_df = trail_results_df.copy()
        for param_name, param_val in trail_params.items():
            trail_params_and_results_df[param_name] = param_val
        columns_order = list(trail_params.keys()) + ['eval_iter_index', 'score']
        trail_params_and_results_df = trail_params_and_results_df[columns_order]
        all_trails_dfs.append(trail_params_and_results_df)
    experiment_results_df = pd.concat(all_trails_dfs)

    experiment_results_folder_path = get_experiment_results_folder_path(experiment_id)
    experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    experiment_results_df.to_csv(experiment_results_folder_path / 'results.csv', index=False)
    experiment_results_df.to_html(experiment_results_folder_path / 'results.html', index=False)
    with open(experiment_results_folder_path / 'experiment_extra_details.json', 'w') as f:
        json.dump(experiment_extra_details, f, indent=4)


def get_experiment_results_folder_path(experiment_id) -> Path:
    return Path(__file__).parent / 'results' / experiment_id


if __name__ == '__main__':
    # run_experiment(
    #     rules='all',
    #     top_ns=(8, 9),
    #     distortion_ratios=(0.1, 0.25, 0.5),
    #     eval_iterations_per_rule=20,
    #     random_seed=42
    # )
    # run_experiment(
    #     rules='all',
    #     top_ns=(9,),
    #     distortion_ratios=(0.1, 0.25, 0.5),
    #     eval_iterations_per_rule=20,
    #     random_seed=42
    # )
    run_experiment(
        rules={'plurality', 'borda', 'veto'},
        voter_models=('random', 'gaussian', 'multinomial_dirichlet'),
        top_n_percs=(20, 40, 60, 80),
        numbers_voters=(1_000,),
        numbers_candidates=(5,),
        distortion_ratios=(0.2, 0.5),
        eval_iterations_per_rule=2,
        random_seed=42
    )
