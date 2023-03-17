import numpy as np
from utils import lower_bound, upper_bound

class SafetyViolationSimulator():
    '''
    This class is designed to simulate times to safety violations given
        parameters for the blockchain,
        reset policy (time to wait before resetting the block to build the adversarial chain on),
        number of trials to run with each reset policy
    - to record expected values of time for a safety violation for different reset policies and
    - to find the reset policy that minimizes the time for a safety violation
    '''
    def __init__(self, start_reset_policy=8, end_reset_policy=10**3, num_trials=10**3, delta=0, K=6, λ=1, rho=0.7):
        '''
        initializes the simulator with the following parameters
        start_reset_policy: inclusive limit to reset policy to test(increments from start_reset_policy to end_reset_policy inclusive)
        end_reset_policy: inclusive limit to reset policy to test (increments from start_reset_policy to end_reset_policy inclusive)
        num_trials: number of trials to conduct to find the avg time for safety violation for each reset policy
        K: depth of confirmation
        λ: total mining rate
        rho: proportion of honest mining rate // (1- rho) == proportion of adversarial mining rate
        arho: 1 - rho // upperbounded by delta and h
        '''
        self.start_reset_policy = start_reset_policy
        self.end_reset_policy = end_reset_policy
        self.num_trials = num_trials
        self.delta = delta
        self.K = K
        self.λ = λ
        self.rho = rho
        self.arho = 1-self.rho
        
        
        '''
        upperbound for a by h and delta
        a < h / (1 + delta * h)
        '''
        h = self.rho * self.λ
        a = self.arho * self.λ
        if not a < h/(1+self.delta*h):
            a = h/(1+self.delta*h)
            self.arho = a / self.λ
        # print(f"{lower_bound(self.K, self.rho)} < P(safety violation) ≤ {upper_bound(self.K, self.rho, self.λ, self.delta)}\n")
        # print("Simulation begins.\n")
        # print(f"end_reset_policy={self.end_reset_policy}\tnum_trials={self.num_trials}\tconfirmation depth={self.K}\tmax delay={self.delta}\ttotal mining rate={self.λ}\thonest mining proportion={self.rho}")
        
         
    def trigger_safety_violation(self, reset_policy):
        '''
        finds time for a safety violation of a block
        Args {
            reset_policy: time to wait before resetting the block to build the adversarial chain on (block to attack for safety violation)
            (safety the first honest child block of this reset-block will be violated)
        }
        Returns {
            time for a safety violation of a block given reset_policy and initial parameters
        }
        '''

        time = 0 # global timekeeper
        loop_time = 0 # in-loop timekeeper
        safety_violation = False # boolean for whether a safety_violation has occurred
        
        adv_num = 0 # number of adversary blocks within reset frame
        hon_num = 0 # number of honest blocks within reset frame
        total_hon_num = 0 # total number of honest blocks observed
        last_hon_time = 0 # time at which the last honest block was mined and propagated
        # by setting to zero, assume that the first block mined was honest
        iter_num = 1
        while not safety_violation: # find minimum time for safety violation in this trial
            inter_mt = np.random.exponential(scale=1/self.λ) # exponential inter_mining times
            loop_time += inter_mt
            time += inter_mt
            is_adversary = np.random.binomial(1, self.arho)
            if is_adversary: # adversarial block
                adv_num += 1
            else: # honest block
                if time - last_hon_time > self.delta: # if mined within delta, can't build up on height
                    hon_num += 1
                    total_hon_num += 1
                    last_hon_time = time
            # print(f'adv_num: {adv_num}\n')
            # print(f'hon_num: {hon_num}\n')
            if adv_num >= hon_num and hon_num >= self.K: # check for safety violation
                safety_violation = True
                # print(f'SAFETY VIOLATION\ntime: {time}\nadv_num: {adv_num}\nhon_num: {hon_num}')
            if loop_time >= reset_policy: # check for reset timeout
                # print(f'RESET\nadv_num: {adv_num}\nhon_num: {hon_num}')
                loop_time = 0
                adv_num = 0
                hon_num = 0
                iter_num += 1
        return time, total_hon_num, iter_num, total_hon_num/iter_num
    
    def expected_violation_time(self, reset_policy):
        '''
        simulates time for a safety violation with given reset policy num_trials times
        Returns {
            expected value of time for safety violation with given reset policy after trying num_trials times
        }
        '''
        violation_times = []
        hon_nums = []
        iter_nums = []
        h_per_iter_nums = []
        for _ in range(self.num_trials): # conduct multiple trials
            v_time, h_num, iter_num, h_per_iter_num = self.trigger_safety_violation(reset_policy)
            violation_times.append(v_time) # record minimum time for safety violation in this trial
            hon_nums.append(h_num)
            iter_nums.append(iter_num)
            h_per_iter_nums.append(h_per_iter_num)
        print(f'simulation with reset_policy = {reset_policy} complete')
        return np.mean(violation_times), np.mean(hon_nums), np.mean(iter_nums), np.mean(h_per_iter_nums)
        # find avg time of minimum times to safety violation with a paraticular reset policy and avg # of honest blocks mined
    
    def min_reset_policy_violation_time(self):
        '''
        runs expected_violation_time with a range of reset_policies
        to find the policy that produces the minimum time for a safety violation
        Returns {
        reset policy that produced the minimum time for a safety violation,
        minimum expected time for a a safety violation (produced by the returned reset policy)
        }
        '''
        expected_min_violation_times = []
        expected_hon_nums = []
        expected_iter_nums = []
        expected_hon_iter_nums = []
        for reset_policy in range(self.start_reset_policy, self.end_reset_policy+1): # iterate through different reset policy times
            avg_violation_time, avg_hon_num, avg_iter_num, avg_hon_iter_num = self.expected_violation_time(reset_policy)
            expected_min_violation_times.append(avg_violation_time)
            expected_hon_nums.append(avg_hon_num)
            expected_iter_nums.append(avg_iter_num)
            expected_hon_iter_nums.append(avg_hon_iter_num)
            # find avg time of minimum times to safety violation with a paraticular reset policy
        
        expected_min_violation_times = np.array(expected_min_violation_times)
        min_idx = np.argmin(expected_min_violation_times)
        
        return range(self.start_reset_policy, self.end_reset_policy)[min_idx],\
                expected_min_violation_times[min_idx],\
                expected_min_violation_times,\
                expected_hon_nums[min_idx],\
                np.array(expected_hon_nums),\
                expected_iter_nums[min_idx],\
                np.array(expected_iter_nums),\
                expected_hon_iter_nums[min_idx],\
                np.array(expected_hon_iter_nums)
        

if __name__ == "__main__":
    start_reset_policy = 30 # inclusive limit to reset policy to test (increments from start_reset_policy to end_reset_policy inclusive)
    end_reset_policy = 100 # inclusive limit to reset policy to test (increments from start_reset_policy to end_reset_policy inclusive)
    num_trials = 10 ** 3 # number of trials to conduct to find the avg time for a safety violation for each reset policy
    K = 6 # depth of confirmation
    delta = 5 # maximum propagation delay
    λ = 1 # total mining rate (block/s)
    rho = 0.7 # proportion of honest mining rate
    # proportion of adversary mining rate = 1 - rho
    
    svs = SafetyViolationSimulator(start_reset_policy=start_reset_policy, end_reset_policy=end_reset_policy, num_trials=num_trials, delta=delta, K=K, λ=λ, rho=rho)
    min_reset_policy, min_expected_violation_time, expected_violation_times, min_expected_hon_num, expected_hon_nums, min_expected_iter_num, expected_iter_nums, min_expected_hon_iter_num, expected_hon_iter_nums = svs.min_reset_policy_violation_time()
    # print(f'\nreset policy for minimum expected time for a safety violation:\n{min_reset_policy}')
    # print(f'\nminimum expected time for a safety violation:\n{min_expected_violation_time}')
    # print(f'\nexpected violation times at reset policy [0, {end_reset_policy}):\n{expected_violation_times}')
    with open(f'./simulation_{delta}.txt', 'a+') as file:
        file.write(f'\n\nK={K}\t\t∆={delta}\t\tλ={λ}\t\trho={rho}')
        file.write(f'\nexpected violation times at reset policy\t= [{start_reset_policy}, {end_reset_policy}]')
        file.write(f'\nnumber of trials for each reset policy\t\t= {num_trials}')
        file.write(f'\nreset policy for minimum expected time for a safety violation:\n\t{min_reset_policy}')
        file.write(f'\nminimum expected time for a safety violation:\n\t{min_expected_violation_time}')
        file.write(f'\nexpected violation times at reset policy range({start_reset_policy}, {end_reset_policy+1}):\n{expected_violation_times}')
        file.write(f'\nexpected number of honest blocks observed before a safety violation:\n\t{min_expected_hon_num}')
        file.write(f'\nexpected number of honest blocks observed at reset policy range({start_reset_policy}, {end_reset_policy+1}):\n{expected_hon_nums}')
        file.write(f'\nexpected number of iterations before a safety violation:\n\t{min_expected_iter_num}')
        file.write(f'\nexpected number of iterations observed at reset policy range({start_reset_policy}, {end_reset_policy+1}):\n{expected_iter_nums}')
        file.write(f'\nexpected number of honest blocks per iteration observed before a safety violation:\n\t{min_expected_hon_iter_num}')
        file.write(f'\nexpected number of honest blocks per iteration observed at reset policy range({start_reset_policy}, {end_reset_policy+1}):\n{expected_hon_iter_nums}')