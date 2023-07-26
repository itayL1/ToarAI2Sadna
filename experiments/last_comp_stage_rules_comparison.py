import json
from pathlib import Path
from typing import Collection, Union, Literal, Optional, Set, List
from uuid import uuid4

import dask
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
    **{
        f'borda_gamma_{gamma}': build_borda_gamma_rule(gamma)
        for gamma in (0.975, 0.75, 0.6, 0.25)
    },
    **{
        f'k_approval_k_{k}': build_k_approval_rule(k)
        for k in (2, 3, 4, 5)
    },
}


def run_experiment(
    rules: Union[Literal['all'], Set[str]],
    top_ns: Collection[int],
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
        dict(rule_name=rule_name, topn=topn, distortion_ratio=distortion_ratio)
        for rule_name in rules
        for topn in top_ns
        for distortion_ratio in distortion_ratios
    ]
    trails_results = _run_trails_in_parallel(trails_params, eval_iterations_per_rule, random_seed)

    _store_experiment_results(experiment_id, trails_results, experiment_details=dict(
        rules=list(rules), top_ns=list(top_ns), distortion_ratios=list(distortion_ratios),
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
    topn = trail_params['topn']
    distortion_ratio = trail_params['distortion_ratio']

    assert rule_name in RULE_NAME_TO_FUNC, f"unknown rule: '{rule_name}'"
    rule_func = RULE_NAME_TO_FUNC[rule_name]

    trail_results_df = eval_rule(
        rule_func=rule_func,
        topn=topn,
        distortion_ratio=distortion_ratio,
        eval_iterations_count=eval_iterations_per_rule,
        random_seed=random_seed,
        print_results=False,
        verbose=False
    )

    ret = dict(trail_params=trail_params, trail_results_df=trail_results_df)
    return ret


def _store_experiment_results(experiment_id: str, trails_results: Collection[dict], experiment_details: dict):
    all_trails_results_dfs = []
    for trail_results in trails_results:
        trail_params = trail_results['trail_params']
        trail_results_df = trail_results['trail_results_df']
        trail_results_df = trail_results_df.copy()
        trail_params_json = json.dumps(trail_params)
        trail_results_df['trail_params'] = trail_params_json
        all_trails_results_dfs.append(trail_results_df)
    experiment_results_df = pd.concat(all_trails_results_dfs)

    experiment_results_folder_path = Path(__file__).parent / 'results' / experiment_id
    experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    experiment_results_df.to_csv(experiment_results_folder_path / 'results.csv', index=False)
    experiment_results_df.to_html(experiment_results_folder_path / 'results.html', index=False)
    with open(experiment_results_folder_path / 'experiment_details.json') as f:
        json.dump(experiment_details, f, indent=4)


if __name__ == '__main__':
    run_experiment(
        rules='all',
        top_ns=(8, 9),
        distortion_ratios=(0.1, 0.25, 0.5),
        eval_iterations_per_rule=20,
        random_seed=42
    )
    # run_experiment(
    #     rules={'plurality', 'borda', 'veto'},
    #     top_ns=(9,),
    #     distortion_ratios=(0.2, 0.5),
    #     eval_iterations_per_rule=2,
    #     random_seed=42
    # )
