import numpy as np
import random as rand


def homogenous(r,T):
    """
    :param r:  Firing rate (Hz)
    :param T:  End time (start = 0). Only last entry will be beyond this time (s)
    """
    t = 0
    while t < T:
        t = t - np.log(rand.random()) / r
        yield t

def homogenous_aslist(*args):
    return list(homogenous(*args))