import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.core.display import HTML
from IPython.display import display

from experiments.last_comp_stage_rules_comparison import get_experiment_results_folder_path


def display_experiment_results(experiment_id: str):
    experiment_results_folder = get_experiment_results_folder_path(experiment_id)
    experiment_results_df = pd.read_csv(experiment_results_folder / 'results.csv')

    _plot_main_rules_performance_comparison_graph(experiment_results_df)


def _plot_main_rules_performance_comparison_graph(experiment_results_df: pd.DataFrame):
    topn_stats_per_eval_subgroup_df = experiment_results_df\
        .groupby(['topn', 'distortion_ratio', 'rule_name'])\
        .agg({"score": [np.mean, np.std]})\
        .reset_index()
    topn_stats_per_eval_subgroup_df['score_mean'] = topn_stats_per_eval_subgroup_df['score']['mean']
    topn_stats_per_eval_subgroup_df['score_std'] = topn_stats_per_eval_subgroup_df['score']['std']
    topn_stats_per_eval_subgroup_df.drop(columns=['score'], inplace=True)

    for (topn, distortion_ratio), rule_stats_df in topn_stats_per_eval_subgroup_df.groupby(['topn', 'distortion_ratio']):
        comparison_title = f"Rule scores results comparison (topn={topn}, distortion_ratio={distortion_ratio})"
        display(HTML(f"<h2>*** {comparison_title} ***</h2>"))

        rule_stats_sorted_df = rule_stats_df.sort_values(by='score_mean', ascending=False)

        x = list(rule_stats_sorted_df['rule_name'])
        y = list(rule_stats_sorted_df['score_mean'])
        yerr = list(rule_stats_sorted_df['score_std'])
        rule_stats_df.sort_values(by='rule_name')

        plt.rcParams["figure.figsize"] = (12, 4)
        plt.rc('lines', linestyle='None')
        plt.xticks(rotation=45)
        plt.title(comparison_title)
        plt.xlabel('Rule')
        plt.ylabel('Mean score (topn)')
        plt.errorbar(x, y, yerr=yerr, marker='o')
        plt.show()
        plt.close()

        display(rule_stats_sorted_df.round(1))


if __name__ == '__main__':
    display_experiment_results(
        experiment_id='31c504ea05c643e88433bc22474dd159'
    )
