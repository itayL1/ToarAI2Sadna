from typing import Callable, Any

import pandas as pd

from experiments.last_comp_stage_rules_comparison import new_experiment_id, get_experiment_results_folder_path


def adjust_experiment_results(experiment_id: str, adjustment_func: Callable[[pd.DataFrame], Any]):
    input_results_folder_path = get_experiment_results_folder_path(experiment_id)
    input_experiment_results_df = pd.read_csv(input_results_folder_path / 'results.csv')

    adjusted_experiment_results_df = adjustment_func(input_experiment_results_df)

    filtered_experiment_id = new_experiment_id()
    filtered_experiment_results_folder_path = get_experiment_results_folder_path(filtered_experiment_id)
    filtered_experiment_results_folder_path.mkdir(parents=False, exist_ok=False)
    adjusted_experiment_results_df.to_csv(filtered_experiment_results_folder_path / 'results.csv', index=False)
    print(f"done. adjusted_experiment_id: '{filtered_experiment_id}'")


def _rename_stv_rule_elishay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['rule_name'] = df['rule_name'].str.replace('stv_rule_elishay', 'stv')
    return df


if __name__ == '__main__':
    adjust_experiment_results(
        experiment_id='2968e846609248f494c59e035168d326',
        adjustment_func=_rename_stv_rule_elishay
    )
