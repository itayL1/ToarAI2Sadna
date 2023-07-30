import json
from collections import defaultdict
from typing import List, Tuple, Collection

import numpy as np
import pandas as pd
import datapane as dp
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

    _show_results_df_head(experiment_results_df)

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

    _show_trail_inferable_subgroup_to_best_rules(experiment_results_df)

    high_distortion_ratio_condition = experiment_results_df['distortion_ratio'] >= 0.8
    high_distortion_ratio_subgroup_df = experiment_results_df[high_distortion_ratio_condition]
    not_high_distortion_ratio_subgroup_df = experiment_results_df[~high_distortion_ratio_condition]
    _plot_rules_winnings_comparison_graph(
        high_distortion_ratio_subgroup_df,
        graph_title=f"high distortion ratio trails"
    )
    _plot_rules_winnings_comparison_graph(
        not_high_distortion_ratio_subgroup_df,
        graph_title=f"not high distortion ratio trails"
    )


def _show_results_df_head(experiment_results_df: pd.DataFrame):
    _display_title(f"results CSV head (shape={experiment_results_df.shape})", main_else_secondary=True)
    display(experiment_results_df.head(10))


def _plot_rules_winnings_comparison_graph(relevant_results_df: pd.DataFrame, graph_title: str):
    _display_title(graph_title, main_else_secondary=True)
    score_stats_per_subgroup_df = _results_to_score_stats_per_subgroup(
        relevant_results_df, subgroup_columns=DATASET_SETUP_DETAILS_COLUMNS)

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
    plt.title("Mean winnings score per rule")
    plt.xlabel('Rule')
    plt.ylabel('Accumulated winnings score')
    plt.bar(x, y)
    plt.show()
    plt.close()

    print(json.dumps(rule_to_mean_winnings_score, indent=4))


def _results_to_score_stats_per_subgroup(
    relevant_results_df: pd.DataFrame, subgroup_columns: Collection[str]
) -> pd.DataFrame:
    score_stats_per_subgroup_df = relevant_results_df \
        .groupby(by=[*subgroup_columns, 'rule_name']) \
        .agg({"score": [np.mean, np.std]}) \
        .reset_index()
    score_stats_per_subgroup_df['score_mean'] = score_stats_per_subgroup_df['score']['mean']
    score_stats_per_subgroup_df['score_std'] = score_stats_per_subgroup_df['score']['std']
    score_stats_per_subgroup_df.drop(columns=['score'], inplace=True)
    return score_stats_per_subgroup_df


def _calc_rule_to_winnings_score_in_trail_mean(trail_mean_df):
    score_to_rules_ordered_by_score_desc = _calc_ordered_score_to_rules(trail_mean_df)

    number_of_unique_scores = len(score_to_rules_ordered_by_score_desc)
    rule_name_to_winnings_score_0_to_1 = {
        rule_name: (number_of_unique_scores - rank_0_based) / number_of_unique_scores
        for rank_0_based, (score, rule_names) in
        enumerate(score_to_rules_ordered_by_score_desc)
        for rule_name in rule_names
    }
    return rule_name_to_winnings_score_0_to_1


def _calc_ordered_score_to_rules(trail_mean_df) -> List[Tuple[float, List[str]]]:
    score_to_rules = defaultdict(list)
    for _, row in trail_mean_df.iterrows():
        score_to_rules[row['score_mean'][0]].append(row['rule_name'][0])
    score_to_rules_ordered_by_score_desc = sorted(list(score_to_rules.items()), key=lambda kvp: kvp[0], reverse=True)
    return score_to_rules_ordered_by_score_desc


def _show_trail_inferable_subgroup_to_best_rules(relevant_results_df: pd.DataFrame):
    inferable_subgroup_columns = _without(DATASET_SETUP_DETAILS_COLUMNS, ('voters_model', 'topn_perc', 'topn_actual'))
    relevant_results_without_borda_veto_hybrid_rule_df = relevant_results_df[
        relevant_results_df['rule_name'] != 'borda_veto_hybrid_rule'
    ]
    score_stats_per_subgroup_df = _results_to_score_stats_per_subgroup(
        relevant_results_without_borda_veto_hybrid_rule_df, subgroup_columns=inferable_subgroup_columns
    )

    trail_subgroup_to_best_rules_rows = []
    for group_key, trail_mean_df in score_stats_per_subgroup_df.groupby(by=[*inferable_subgroup_columns]):
        score_to_rules_ordered_by_score_desc = _calc_ordered_score_to_rules(trail_mean_df)
        best_trail_rules = score_to_rules_ordered_by_score_desc[0][1]

        row_dict = {
            **{
                key_col: group_key[i]
                for i, key_col in enumerate(inferable_subgroup_columns)
            },
            'best_rules': str(best_trail_rules)
        }
        trail_subgroup_to_best_rules_rows.append(row_dict)

    inferable_subgroup_to_best_rules_df = pd.DataFrame(data=trail_subgroup_to_best_rules_rows)

    _display_title("inferable_subgroup_to_best_rules_df", main_else_secondary=True)
    display(dp.DataTable(inferable_subgroup_to_best_rules_df))

    _display_title("subgroups_where_borda_doesnt_win_df", main_else_secondary=False)
    subgroups_where_borda_doesnt_win_df = inferable_subgroup_to_best_rules_df[
        ~inferable_subgroup_to_best_rules_df['best_rules'].str.contains("'borda'")
    ]
    display(dp.DataTable(subgroups_where_borda_doesnt_win_df))

    _display_title("subgroups_with_high_distortion_ratio_df", main_else_secondary=False)
    subgroups_with_high_distortion_ratio_df = inferable_subgroup_to_best_rules_df[
        (inferable_subgroup_to_best_rules_df['distortion_ratio'] >= 0.6)
    ]
    subgroups_with_high_distortion_ratio_df = subgroups_with_high_distortion_ratio_df.copy()
    subgroups_with_high_distortion_ratio_df['veto_wins'] =\
        subgroups_with_high_distortion_ratio_df['best_rules'].str.contains("'veto'")
    subgroups_with_high_distortion_ratio_df['borda_wins'] =\
        subgroups_with_high_distortion_ratio_df['best_rules'].str.contains("'borda'")
    subgroups_with_high_distortion_ratio_df['#winning_rules'] =\
        subgroups_with_high_distortion_ratio_df['best_rules'].apply(lambda br: len(json.loads(br.replace("'", '"'))))
    display(dp.DataTable(subgroups_with_high_distortion_ratio_df))


def _without(collection: Collection, excluded_items: Collection) -> list:
    return [item for item in collection if item not in excluded_items]


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
