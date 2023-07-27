import random

import numpy as np


def set_global_random_seed(random_seed: int):
    random.seed(random_seed)
    np.random.seed(random_seed)
