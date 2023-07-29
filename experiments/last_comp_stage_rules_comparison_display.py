import json
from collections import defaultdict

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

    _plot_rules_winnings_comparison_graph(experiment_results_df, graph_title="all dataset setups")
    distribution_voter_models = sorted(set(experiment_results_df['voters_model']))
    for distribution_voter_model in distribution_voter_models:
        voter_model_trails_df = experiment_results_df[
            experiment_results_df['voters_model'] == distribution_voter_model
        ]
        _plot_rules_winnings_comparison_graph(
            voter_model_trails_df,
            graph_title=f"distribution_voter_model = '{distribution_voter_model}' trails"
        )

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
        _display_title(comparison_title, main_else_secondary=True)

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
    _display_title(graph_title, main_else_secondary=True)
    score_stats_per_subgroup_df = relevant_results_df \
        .groupby(by=[*DATASET_SETUP_DETAILS_COLUMNS, 'rule_name']) \
        .agg({"score": [np.mean, np.std]}) \
        .reset_index()
    score_stats_per_subgroup_df['score_mean'] = score_stats_per_subgroup_df['score']['mean']
    score_stats_per_subgroup_df['score_std'] = score_stats_per_subgroup_df['score']['std']
    score_stats_per_subgroup_df.drop(columns=['score'], inplace=True)

    # _display_title("top 3 wining rules per subgroup", main_else_secondary=False)
    # top3_winning_rules_per_subgroup_df = score_stats_per_subgroup_df\
    #     .groupby(by=[*DATASET_SETUP_DETAILS_COLUMNS]) \
    #     .apply(lambda group: group.sort_values(["score_mean"], ascending=False).head(3))\
    #     .sort_index().reset_index(drop=True)
    # display(top3_winning_rules_per_subgroup_df)

    comparison_graph_title = "winnings count per rule (borda-ish)"
    # _display_title(comparison_graph_title, main_else_secondary=False)
    rule_to_accumulated_winnings_score = defaultdict(lambda: 0)
    sum_components_count = 0
    for _, trail_mean_df in score_stats_per_subgroup_df.groupby(by=[*DATASET_SETUP_DETAILS_COLUMNS]):
        sum_components_count += 1

        rule_name_to_winnings_score_0_to_1 = _calc_rule_to_winnings_score_in_trail_mean(trail_mean_df)
        for rule_name, winnings_score_0_to_1 in rule_name_to_winnings_score_0_to_1.items():
            rule_to_accumulated_winnings_score[rule_name] += winnings_score_0_to_1

    rule_to_mean_winnings_score = {
        rule_name: round(accumulated_winnings_score / sum_components_count, 4)
        for rule_name, accumulated_winnings_score in rule_to_accumulated_winnings_score.items()
    }
    rule_to_mean_winnings_score = _sort_dict_by_vals(rule_to_mean_winnings_score, ascending=False)
    x = list(rule_to_mean_winnings_score.keys())
    y = list(rule_to_mean_winnings_score.values())

    plt.rcParams["figure.figsize"] = (12, 4)
    plt.rc('lines', linestyle='None')
    plt.xticks(rotation=90)
    plt.title(comparison_graph_title)
    plt.xlabel('Rule')
    plt.ylabel('Accumulated winnings score')
    plt.bar(x, y)
    plt.show()
    plt.close()

    print(json.dumps(rule_to_mean_winnings_score, indent=4))


def _calc_rule_to_winnings_score_in_trail_mean(group_df):
    score_to_rules = defaultdict(list)
    for _, row in group_df.iterrows():
        score_to_rules[row['score_mean'][0]].append(row['rule_name'][0])
    number_of_unique_scores = len(score_to_rules)
    rule_name_to_winnings_score_0_to_1 = {
        rule_name: (number_of_unique_scores - rank_0_based) / number_of_unique_scores
        for rank_0_based, (score, rule_names) in
        enumerate(sorted(list(score_to_rules.items()), key=lambda kvp: kvp[0], reverse=True))
        for rule_name in rule_names
    }
    return rule_name_to_winnings_score_0_to_1


def _display_title(title_text: str, main_else_secondary: bool):
    title_html_tag = 'h2' if main_else_secondary else 'h4'
    display(HTML(f"<{title_html_tag}>*** {title_text} ***</{title_html_tag}>"))


def _sort_dict_by_vals(dict_: dict, ascending: bool) -> dict:
    return {
        key: val for key, val
        in sorted(dict_.items(), key=lambda kvp: kvp[1], reverse=not ascending)
    }


if __name__ == '__main__':
    display_experiment_results(
        experiment_id='06d7546459494be9b40ebc6bd2de59b8'
    )
