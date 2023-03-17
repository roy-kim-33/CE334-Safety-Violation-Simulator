import numpy as np
from safety_violation_sim import SafetyViolationSimulator
import pprint

def test_delta(start_reset_policy=8, end_reset_policy=10**3, num_trials=10**3, K=6, λ=1, rho=0.7, min_delta=0, max_delta=10, num_iterations=10**3):
    min_violation_times_by_delta = {}
    # 'reset_policy': list of reset policies that map to 'min_exp_time' at the same index
    # 'min_exp_time': list of reset policies that map to 'reset_policy' at the same index
    # 'avg_min_exp_time': average of 'min_exp_time'
    for delta in range(min_delta, max_delta+1): # maximum propagation delay
        # print('-'*100)
        print(f'TESTING ∆={delta}')
        print('-'*100)
        # with open('./testing_deltas.txt', 'a+') as file:
        #         file.write('\n\n\nParameters {')
        #         file.write(f'\nK={K}\t\t∆={delta}\t\tλ={λ}\t\trho={rho}')
        #         file.write(f'\nexpected violation times at reset policy\t= range({end_reset_policy})')
        #         file.write(f'\nnumber of trials for each reset policy\t\t= {num_trials}')
        #         file.write('\n}')
        for i in range(num_iterations):
            print(f'iteration: {i+1}...')
            svs = SafetyViolationSimulator(start_reset_policy=start_reset_policy, end_reset_policy=end_reset_policy, num_trials=num_trials, delta=delta, K=K, λ=λ, rho=rho)
            min_reset_policy, min_expected_violation_time, expected_min_violation_times = svs.min_reset_policy_violation_time()
            
            if delta in min_violation_times_by_delta:
                min_violation_times_by_delta[delta]['reset_policy'].append(min_reset_policy)
                min_violation_times_by_delta[delta]['min_exp_time'].append(min_expected_violation_time)
            else:
                min_violation_times_by_delta[delta] = {}
                min_violation_times_by_delta[delta]['reset_policy'] = [min_reset_policy]
                min_violation_times_by_delta[delta]['min_exp_time'] = [min_expected_violation_time]
        print('DONE!')
        for delta in min_violation_times_by_delta:
            min_violation_times_by_delta[delta]['avg_min_exp_time'] = np.mean(min_violation_times_by_delta[delta]['min_exp_time'])
        # pprint.pprint(min_violation_times_by_delta)
    return min_violation_times_by_delta
    
        

if __name__ == "__main__":
    start_reset_policy = 8 # inclusive limit to reset policy to test (increments from start_reset_policy to end_reset_policy inclusive)
    end_reset_policy = 10 ** 3 # inclusive limit to reset policy to test (increments from 0 to end_reset_policy exclusive)
    num_trials = 10 ** 3 # number of trials to conduct to find the avg time for a safety violation for each reset policy
    K = 6 # depth of confirmation
    λ = 1 # total mining rate (block/s)
    rho = 0.7 # proportion of honest mining rate
    # proportion of adversary mining rate = 1 - rho
    min_delta = 0
    max_delta = 0
    num_iterations = 1
    min_violation_times_by_delta = test_delta(start_reset_policy, end_reset_policy, num_trials, K, λ, rho, min_delta, max_delta, num_iterations)
    with open(f'./testing_deltas{min_delta}-{max_delta}.txt', 'a+') as file:
       file.write(f"dictionary containing info about minimum time for a safety violation by different delta values\
                   \nmaps delta to a dicdtionary of 'min_exp_time', 'reset_policy', 'avg_min_exp_time' where\
                   \n\t'reset_policy': list of reset policies that map to 'min_exp_time' at the same index\
                   \n\t'min_exp_time': list of reset policies that map to 'reset_policy' at the same index\
                   \n\t'avg_min_exp_time': average of 'min_exp_time'")
       file.write(f'\n\n{pprint.pformat(min_violation_times_by_delta)}\n\n\n')