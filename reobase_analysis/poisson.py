import numpy as np
import random as rand


def homogeneous(r, T):
    """
    :param r:  Firing rate (units are unimportant as long as they match)
    :param T:  End time (start = 0). Only last entry will be beyond this time
    """
    t = 0
    while t < T:
        t = t - np.log(rand.random()) / float(r)
        yield t

def homogeneous_list(*args):
    return list(homogeneous(*args))

