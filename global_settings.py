############## Training Variables ############
TOTAL_TRAIN_STEPS = 10000
SAVE_RESULT_FREQ_DDoS = 1000

############## LINK Variables ########
LINK_BANDWIDTH = 10 * 1024 * 1024
RESOURCE_BANDWIDTH = 1.2 * LINK_BANDWIDTH

GB_to_KB = 1024*1024
BENIGN_DROP_LOSS = 15000 ##### Cost due to Per GB Traffic lost
BENIGN_DELAY_LOSS = 2500 ###### Cost due to Per GB Traffic Delay
AVG_REWARD = (RESOURCE_BANDWIDTH/20)*BENIGN_DROP_LOSS

####### Define global variables ###############
defense_list_ratios = [0.33,0.66,1.0]
limit_function_type = [0,1,2]
limit_function_map = {-1:None,0:'Convex',1:'Concave',2:'Traditional'}

############ Action List #############
defense_space = []

########### Observation List #######
observation_space = []

########## Observation Space ############
link_utilization = [0.33,0.66,1.0]
Drop_ratio = [0.33,0.66,1.0]

########### Convex Limit Function ################
''' y=(nx)^v, where v and n are constants and x is the risk score
    Tune v to get the optimal function --> Binary Search'''
convex_limit_function_type = 0
convex_n,convex_v = 2,2.5
concave_limit_function_type = 0
concave_n,concave_v = 4,0.6

########## Traffic distribution ###################
traffic_dist_risk_scores = [0.0 for i in range(101)]
benign_across_risk_scores = [0.0 for i in range(101)]
attack_across_risk_scores = [0.0 for i in range(101)]
affordable_volume_error_threshold = 0.01

############## Nornalize the vector ##################
def normalize_vector_by_max(vector):
    ''' This function normalizes the functions by the max value'''
    max_value = max(vector)
    for i in range(len(vector)):
        vector[i] /= max_value


