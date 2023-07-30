from typing import Callable, Any

import pandas as pd

from experiments.last_comp_stage_rules_comparison import new_experiment_id, get_experiment_results_folder_path


def filter_experiment_results(experiment_id: str, filter_building_func: Callable[[pd.DataFrame], Any]):
    input_results_folder_path = get_experiment_results_folder_path(experiment_id)
    input_experiment_results_df = pd.read_csv(input_results_folder_path / 'results.csv')

    results_filter = filter_building_func(input_experiment_results_df)
    filtered_experiment_results_df = input_experiment_results_df[results_filter]

    filtered_experiment_id = new_experiment_id()
    filtered_experiment_results_folder_path = get_experiment_results_folder_path(filtered_experiment_id)
    filtered_experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    filtered_experiment_results_df.to_csv(filtered_experiment_results_folder_path / 'results.csv', index=False)
    print(f"done. filtered_experiment_id: '{filtered_experiment_id}'")


if __name__ == '__main__':
    filter_experiment_results(
        experiment_id='df327e3a66c6418eafd3b3df1f36a1b1',
        filter_building_func=lambda df: df['rule_name'] != 'borda_veto_hybrid_rule'
    )
