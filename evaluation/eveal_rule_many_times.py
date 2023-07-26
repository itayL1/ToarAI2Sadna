from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

from evaluation.eval_rule import eval_rule
from rules.borda_rule import borda_rule


def main():
    res_random_seeds_to_dfs = {}
    for i in tqdm(list(range(10))):
        random_seed = (i + 1)
        res_df = eval_rule(
            rule_func=borda_rule,
            topn=10, # not sure yet
            distortion_ratio=0.5, # not sure yet
            eval_iterations_count=10,
            random_seed=random_seed,
            print_results=False,
            verbose=False
        )
        res_random_seeds_to_dfs[random_seed] = res_df

    x = []
    y = []
    e = []
    for random_seed, df in res_random_seeds_to_dfs.items():
        topn_stats = df['topn'].describe()
        x.append(random_seed)
        y.append(topn_stats['mean'])
        e.append(topn_stats['std'])

    plt.errorbar(x, y, e, linestyle='None', marker='^')
    plt.show()


if __name__ == '__main__':
    main()