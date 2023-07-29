import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.core.display import HTML
from IPython.display import display

from experiments.last_comp_stage_rules_comparison import get_experiment_results_folder_path

DATASET_SETUP_DETAILS_COLUMNS = (
    'voters_model',
    'number_voters',
    'number_candidates',
    'distortion_ratio',
    'topn_perc',
    'topn_actual'
)


def display_experiment_results(experiment_id: str):
    experiment_results_folder = get_experiment_results_folder_path(experiment_id)
    experiment_results_df = pd.read_csv(experiment_results_folder / 'results.csv')

    _plot_rules_winnings_comparison_graph(experiment_results_df, graph_title="all dataset setups:")

    # _plot_dataset_setups_rules_performance_comparison_graphs(experiment_results_df)


def _plot_dataset_setups_rules_performance_comparison_graphs(experiment_results_df: pd.DataFrame):
    # todo - split by more dataset details
    topn_stats_per_eval_subgroup_df = experiment_results_df\
        .groupby(['topn_actual', 'topn_perc', 'distortion_ratio', 'rule_name'])\
        .agg({"score": [np.mean, np.std]})\
        .reset_index()
    topn_stats_per_eval_subgroup_df['score_mean'] = topn_stats_per_eval_subgroup_df['score']['mean']
    topn_stats_per_eval_subgroup_df['score_std'] = topn_stats_per_eval_subgroup_df['score']['std']
    topn_stats_per_eval_subgroup_df.drop(columns=['score'], inplace=True)

    for (topn_actual, topn_perc, distortion_ratio), rule_stats_df in topn_stats_per_eval_subgroup_df.groupby(['topn_actual', 'topn_perc', 'distortion_ratio']):
        comparison_title = f"Rule scores results comparison (topn = {topn_actual}[{topn_perc}%], distortion_ratio = {distortion_ratio})"
        _display_title(comparison_title)

        rule_stats_sorted_df = rule_stats_df.sort_values(by='score_mean', ascending=False)

        x = list(rule_stats_sorted_df['rule_name'])
        y = list(rule_stats_sorted_df['score_mean'])
        yerr = list(rule_stats_sorted_df['score_std'])
        rule_stats_df.sort_values(by='rule_name')

        plt.rcParams["figure.figsize"] = (12, 4)
        plt.rc('lines', linestyle='None')
        plt.xticks(rotation=90)
        plt.title(comparison_title)
        plt.xlabel('Rule')
        plt.ylabel('Mean score (topn)')
        plt.errorbar(x, y, yerr=yerr, marker='o')
        plt.show()
        plt.close()

        display_rule_stats_sorted_df = rule_stats_sorted_df.copy()
        display_rule_stats_sorted_df['topn'] = \
            display_rule_stats_sorted_df['topn_actual'].astype(str) + ' (' +\
            display_rule_stats_sorted_df['topn_perc'].astype(str) + '%)'
        display_rule_stats_sorted_df.drop(columns=['topn_actual', 'topn_perc'], inplace=True)
        display(display_rule_stats_sorted_df.round(1))


def _plot_rules_winnings_comparison_graph(relevant_results_df: pd.DataFrame, graph_title: str):
    _display_title(graph_title)
    score_stats_per_subgroup_df = relevant_results_df \
        .groupby(by=[*DATASET_SETUP_DETAILS_COLUMNS, 'rule_name']) \
        .agg({"score": [np.mean, np.std]}) \
        .reset_index()
    score_stats_per_subgroup_df['score_mean'] = score_stats_per_subgroup_df['score']['mean']
    score_stats_per_subgroup_df['score_std'] = score_stats_per_subgroup_df['score']['std']
    score_stats_per_subgroup_df.drop(columns=['score'], inplace=True)

    aaa = score_stats_per_subgroup_df\
        .groupby(by=[*DATASET_SETUP_DETAILS_COLUMNS, 'rule_name']) \
        .apply(lambda group: group.sort_values(["score_mean"], ascending=False).head(3))\
        .sort_index().reset_index(drop=True)
    display(aaa)


def _display_title(title_text: str):
    display(HTML(f"<h2>*** {title_text} ***</h2>"))


if __name__ == '__main__':
    display_experiment_results(
        experiment_id='31c504ea05c643e88433bc22474dd159'
    )
