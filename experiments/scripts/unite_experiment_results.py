from typing import Collection

import pandas as pd

from experiments.last_comp_stage_rules_comparison import new_experiment_id, get_experiment_results_folder_path


def unite_experiment_results(experiment_ids: Collection[str]):
    all_experiments_dfs = []
    for eid in experiment_ids:
        experiment_results_folder_path = get_experiment_results_folder_path(eid)
        experiment_results_df = pd.read_csv(experiment_results_folder_path / 'results.csv')
        all_experiments_dfs.append(experiment_results_df)

    united_experiment_id = new_experiment_id()
    united_experiment_results_folder_path = get_experiment_results_folder_path(united_experiment_id)
    united_experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    united_experiment_results_df = pd.concat(all_experiments_dfs)
    united_experiment_results_df.to_csv(united_experiment_results_folder_path / 'results.csv', index=False)
    print(f"done. united_experiment_id: '{united_experiment_id}'")


if __name__ == '__main__':
    unite_experiment_results(
        experiment_ids=(
            '06d7546459494be9b40ebc6bd2de59b8',
            'a091e1c4edeb4384beb67451ee7d5919',
        )
    )
