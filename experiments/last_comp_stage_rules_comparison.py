import json
from pathlib import Path
from typing import Collection, Union, Literal, Optional, Set, List, Callable
from uuid import uuid4

import dask
import math
import pandas as pd
from compsoc.evaluate import get_rule_utility
from dask.diagnostics import ProgressBar
from tqdm import tqdm

from evaluation.eval_rule import generate_eval_profile
from rules.borda_gamma_rule import build_borda_gamma_rule
from rules.borda_rule import borda_rule
from rules.borda_veto_hybrid_rule import borda_veto_hybrid_rule
from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.k_approval_rule_percentage_version import build_k_approval_rule_percentage_version
from rules.maximin_rule import maximin_rule
from rules.plurality_rule import plurality_rule
from rules.random_rule import random_rule
from rules.simpson_rule import simpson_rule
from rules.stv_rule_elishay import stv_rule_elishay
from rules.veto_rule import veto_rule
from utils.random_utils import set_global_random_seed

RULE_NAME_TO_FUNC = {
    'borda': borda_rule,
    'copeland': copeland_rule,
    'dowdall': dowdall_rule,
    'maximin': maximin_rule,
    'plurality': plurality_rule,
    'simpson': simpson_rule,
    'veto': veto_rule,
    'stv_rule_elishay': stv_rule_elishay,
    'borda_veto_hybrid_rule': borda_veto_hybrid_rule,
    'random': random_rule,
    **{
        f'borda_gamma_{gamma}': build_borda_gamma_rule(gamma)
        for gamma in (0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.25)
    },
    **{
        f'k_approval_{perc}%': build_k_approval_rule_percentage_version(perc)
        for perc in (5, 10, 20, 40, 80)
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
    run_trails_in_parallel: bool,
    random_seed: Optional[int] = None
):
    experiment_id = new_experiment_id()
    print(f"experiment_id: '{experiment_id}'")

    if rules == 'all':
        rules = set(RULE_NAME_TO_FUNC.keys())
    elif not isinstance(rules, set):
        raise ValueError(f"unexpected rules param type: {type(rules)}")

    trails_dataset_setups = [
        dict(
            voters_model=voter_model,
            number_voters=number_voters,
            number_candidates=number_candidates,
            distortion_ratio=distortion_ratio
        )
        for voter_model in voter_models
        for number_voters in numbers_voters
        for number_candidates in numbers_candidates
        for distortion_ratio in distortion_ratios
    ]
    # filter out dataset setups that cause memory leak
    trails_dataset_setups = [
        tds for tds in trails_dataset_setups
        if not (tds['voters_model'] == 'gaussian' and tds['number_candidates'] > 10)
    ]
    trails_params = [
        dict(
            dataset_setup=dataset_setup,
            evaluation_params=[
                dict(
                    rule_name=rule_name,
                    topn_perc=topn_perc,
                    topn_actual=math.ceil(dataset_setup['number_candidates'] * (topn_perc / 100)),
                )
                for rule_name in rules
                for topn_perc in top_n_percs
            ]
        )
        for dataset_setup in trails_dataset_setups
    ]
    trails_results = _run_trails(trails_params, eval_iterations_per_rule, run_trails_in_parallel, random_seed)

    _store_experiment_results(experiment_id, trails_results, experiment_extra_details=dict(
        eval_iterations_per_rule=eval_iterations_per_rule, random_seed=random_seed
    ))


def new_experiment_id():
    return uuid4().hex


def _run_trails(
    trails_params: List[dict],
    eval_iterations_per_rule: int,
    in_parallel: bool,
    random_seed: Optional[int]
) -> Collection[dict]:
    ProgressBar().register()
    _write_jobs_stats_opening_message(trails_params)

    if in_parallel:
        with dask.config.set(scheduler='processes'):
            delayed_results = []
            for trail_params in trails_params:
                trail_task = dask.delayed(_run_dataset_trails_task)(
                    trail_params=trail_params, eval_iterations_per_rule=eval_iterations_per_rule, random_seed=random_seed
                )
                delayed_results.append(trail_task)
            trails_results = dask.compute(*delayed_results)
    else:
        trails_results = []
        with tqdm(total=len(trails_params)) as pabr:
            for trail_params in trails_params:
                pabr.write(f"curr dataset setup: {trail_params['dataset_setup']}")
                trail_results = _run_dataset_trails_task(
                    trail_params=trail_params, eval_iterations_per_rule=eval_iterations_per_rule,
                    random_seed=random_seed, logging_func=pabr.write
                )
                trails_results.append(trail_results)
                pabr.update()

    return trails_results


def _write_jobs_stats_opening_message(trails_params: List[dict]):
    jobs_count = len(trails_params)
    total_trails_count = sum(len(tp['evaluation_params']) for tp in trails_params)
    trails_per_job = round(total_trails_count / jobs_count, 2)
    print(
        f"starting to run requested trails in parallel. total number of jobs: {jobs_count}. "
        f"total number of trails: {total_trails_count} (trails per job: ~{trails_per_job})."
    )


def _run_dataset_trails_task(
    trail_params: dict, eval_iterations_per_rule: int,
        random_seed: Optional[int], logging_func: Optional[Callable] = None
) -> dict:
    if random_seed is not None:
        set_global_random_seed(random_seed)

    iteration_trails_results = []
    failed_iterations_details = []
    for i in range(eval_iterations_per_rule):
        try:
            dataset_profile = generate_eval_profile(**trail_params['dataset_setup'])
        except Exception as ex:
            (logging_func or print)("failed iteration")
            failed_iterations_details.append({'eval_iter_index': i, 'exception_str': str(ex)})
            continue

        for eval_params in trail_params['evaluation_params']:
            rule_name = eval_params['rule_name']
            topn = eval_params['topn_actual']

            should_skip_trail = topn == 0
            if not should_skip_trail:
                assert rule_name in RULE_NAME_TO_FUNC, f"unknown rule: '{rule_name}'"
                rule_func = RULE_NAME_TO_FUNC[rule_name]

                if logging_func:
                    logging_func(f"current trail: {eval_params}")

                iteration_results = get_rule_utility(
                    profile=dataset_profile,
                    rule=rule_func,
                    topn=topn,
                    verbose=False
                )
                iteration_trails_results.append({**eval_params, 'eval_iter_index': i, 'score': iteration_results['topn']})

    assert any(iteration_trails_results), "empty results are unexpected"
    iteration_trails_results_df = pd.DataFrame(data=iteration_trails_results)
    failed_iterations_details_df = pd.DataFrame(data=failed_iterations_details) if any(failed_iterations_details) else pd.DataFrame()
    ret = dict(
        dataset_setup=trail_params['dataset_setup'],
        iteration_trails_results_df=iteration_trails_results_df,
        failed_iterations_details_df=failed_iterations_details_df
    )
    return ret


def _store_experiment_results(experiment_id: str, trails_results: Collection[dict], experiment_extra_details: dict):
    print(f"storing the results of the experiment (experiment_id: '{experiment_id}')")

    all_trails_results_dfs = []
    all_failed_iterations_details_dfs = []
    for trail_results in trails_results:
        dataset_setup = trail_results['dataset_setup']
        iteration_trails_results_df = trail_results['iteration_trails_results_df']

        iteration_trails_results_df = _add_dataset_setup_columns_to_df(
            iteration_trails_results_df, dataset_setup)

        iteration_trails_results_df = _reorder_results_df_columns(
            iteration_trails_results_df, dataset_setup_columns=dataset_setup.keys())
        all_trails_results_dfs.append(iteration_trails_results_df)

        failed_iterations_details_df = trail_results['failed_iterations_details_df']
        failed_iterations_details_df = _add_dataset_setup_columns_to_df(
            failed_iterations_details_df, dataset_setup)
        all_failed_iterations_details_dfs.append(failed_iterations_details_df)

    experiment_results_df = pd.concat(all_trails_results_dfs)
    experiment_failures_df = pd.concat(all_failed_iterations_details_dfs)

    experiment_results_folder_path = get_experiment_results_folder_path(experiment_id)
    experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    experiment_results_df.to_csv(experiment_results_folder_path / 'results.csv', index=False)
    experiment_failures_df.to_csv(experiment_results_folder_path / 'failures.csv', index=False)
    experiment_results_df.to_html(experiment_results_folder_path / 'results.html', index=False)
    experiment_failures_df.to_html(experiment_results_folder_path / 'failures.html', index=False)
    with open(experiment_results_folder_path / 'experiment_extra_details.json', 'w') as f:
        json.dump(experiment_extra_details, f, indent=4)


def _add_dataset_setup_columns_to_df(df: pd.DataFrame, dataset_setup: dict) -> pd.DataFrame:
    df = df.copy()
    if not df.empty:
        for param_name, param_val in dataset_setup.items():
            df[param_name] = param_val
    return df


def _reorder_results_df_columns(
        iteration_trails_results_df: pd.DataFrame, dataset_setup_columns: Collection[str]
) -> pd.DataFrame:
    first_columns = list(dataset_setup_columns)
    last_columns = ['eval_iter_index', 'score']
    other_columns = [
        col for col in iteration_trails_results_df.columns
        if col not in (first_columns + last_columns)
    ]
    columns_order = first_columns + other_columns + last_columns
    iteration_trails_results_df = iteration_trails_results_df[columns_order]
    return iteration_trails_results_df


def get_experiment_results_folder_path(experiment_id) -> Path:
    return Path(__file__).parent / 'results' / experiment_id


if __name__ == '__main__':
    run_experiment(
        rules='all',
        # rules={'borda_veto_hybrid_rule'},
        voter_models=('random', 'gaussian', 'multinomial_dirichlet'),
        top_n_percs=(20, 40, 60, 80),
        numbers_voters=(500, 1_000, 10_000),
        numbers_candidates=(5, 10, 20, 40),
        distortion_ratios=(0.1, 0.25, 0.5, 0.6, 0.7, 0.8, 0.9),
        # distortion_ratios=(0.6, 0.7, 0.8),
        eval_iterations_per_rule=15,
        run_trails_in_parallel=True,
        random_seed=42
    )
