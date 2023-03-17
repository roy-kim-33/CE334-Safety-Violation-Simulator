import numpy as np

def lower_bound(k, rho):
    '''
    returns the lower bound of probability of a safety violoation
    k: depth of confirmation
    rho: fraction of honest mining rate
    '''
    return (1/np.sqrt(k)) * (4*rho*(1-rho))**k

def upper_bound(k, rho, λ, delta):
    '''
    returns the upper bound of probability of a safety violation
    k: depth of confirmation
    rho: fraction of honest mining rate
    λ: total mining rate (block/s)
    delta: block propagation delay upper bound ∆ (s)
    '''
    p = rho * np.exp(-λ*delta)
    return 2 * (1 + np.sqrt(p/(1-p))) * np.power((4*p * (1 - p)), k)