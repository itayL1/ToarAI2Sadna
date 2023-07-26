from typing import Collection, Union, Literal, Optional

from rules.borda_gamma_rule import build_borda_gamma_rule
from rules.borda_rule import borda_rule
from rules.copeland_rule import copeland_rule
from rules.dowdall_rule import dowdall_rule
from rules.k_approval_rule import build_k_approval_rule
from rules.maximin_rule import maximin_rule
from rules.plurality_rule import plurality_rule
from rules.simpson_rule import simpson_rule
from rules.veto_rule import veto_rule
from utils.random_utils import set_global_random_seed

RULE_NAME_TO_FUNC = {
    'borda': borda_rule,
    'copeland_rule': copeland_rule,
    'dowdall_rule': dowdall_rule,
    'maximin_rule': maximin_rule,
    'plurality_rule': plurality_rule,
    'simpson_rule': simpson_rule,
    'veto_rule': veto_rule,
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
    top_ns: Collection[int],
    distortion_ratios: Collection[float],
    rules: Union[Literal['all'], Collection[str]],
    eval_iterations_per_rule: int,
    random_seed: Optional[int] = None,
):
    if random_seed is not None:
        set_global_random_seed(random_seed)


if __name__ == '__main__':
    run_experiment(
        top_ns=(8, 9, 10),
        distortion_ratios=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7),
        rules='all',
        eval_iterations_per_rule=25,
        random_seed=42
    )
