import gym
from gym import spaces
import global_settings
import random

class cyberEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self,defense_list,obsv_list):
        super(cyberEnv, self).__init__()
        self.defense_list = defense_list
        self.observation_list = obsv_list
        self.action_space = spaces.Discrete(len(self.defense_list))
        self.observation_space = spaces.Discrete(len(self.observation_list))
        self.state_space = spaces.Discrete(3)
        self.automated_traffic_drop = 0
        self.traffic_mitigation = 0
        self.benign_traffic_drop = 0
        self.benign_traffic_delay = 0
        self.loss_forced_benign_traffic_drop = 0
        self.loss_automated_benign_traffic_drop = 0
        self.loss_delayed_benign_traffic = 0
        self.ob = 0

    #################### This function takes input from Dr. Qi ################################
    def attack_mode(self):
        ############### Test Modeules ####################
        for i in range(101):
            global_settings.traffic_dist_risk_scores[i] += random.randint(40000,50000) #### In KB
            if i != 100:
                global_settings.benign_across_risk_scores[i] += random.randint(100,int(global_settings.traffic_dist_risk_scores[i]))
            global_settings.attack_across_risk_scores[i] = global_settings.traffic_dist_risk_scores[i] - global_settings.benign_across_risk_scores[i]
            # print('%s >? %s'%(global_settings.RESOURCE_BANDWIDTH,sum(global_settings.traffic_dist_risk_scores)))

        ''' Generate traffic here --> 1. There are 101 possible risk scores [0,100]'''
        ''' Generate traffic volume at each risk score'''
        ''' Defines how many of them are benign'''
        ''' The rest of them are attack'''

    def remove_traffic(self,action_obj):
        # print('Limit Type %s --> Amount %s'%(action_obj.limit_type,action_obj.chosen_limit_vector_ratio))
        for i in range(101):
            global_settings.traffic_dist_risk_scores[i] -= action_obj.chosen_limit_vector_ratio[i]*global_settings.traffic_dist_risk_scores[i]
            self.benign_traffic_drop += action_obj.chosen_limit_vector_ratio[i]*global_settings.benign_across_risk_scores[i]
            global_settings.benign_across_risk_scores[i] -= action_obj.chosen_limit_vector_ratio[i]*global_settings.benign_across_risk_scores[i]
            global_settings.attack_across_risk_scores[i] = global_settings.traffic_dist_risk_scores[i] - global_settings.benign_across_risk_scores[i]

    def reroute_traffic(self, action_obj):
        for i in range(101):
            if action_obj.diverted_traffic_amount <=0:
                break
            action_obj.diverted_traffic_amount -= global_settings.traffic_dist_risk_scores[i]
            self.benign_traffic_delay += global_settings.benign_across_risk_scores[i]
            global_settings.traffic_dist_risk_scores[i] = 0
            global_settings.benign_across_risk_scores[i] = 0
            global_settings.attack_across_risk_scores[i] = 0

    def reset(self):
        global_settings.traffic_dist_risk_scores = [0.0 for i in range(101)]
        global_settings.benign_across_risk_scores = [0.0 for i in range(101)]
        global_settings.attack_across_risk_scores = [0.0 for i in range(101)]
        self.attack_mode()
        return 0

    def step(self,action):
        ''' Drop traffic automatically if over the bandwidth'''
        # print("Time %s"%(self.ob))
        self.ob += 1
        self.benign_traffic_drop = 0
        self.benign_traffic_delay = 0

        self.traffic_mitigation = max(sum(global_settings.traffic_dist_risk_scores) - global_settings.LINK_BANDWIDTH, 0)
        if self.traffic_mitigation > 0:
            action_object = self.defense_list[action]
            action_object.set_limited_traffic_amount(self.traffic_mitigation)
            if action_object.limited_traffic_amount > 0:
                self.remove_traffic(action_object)
            if action_object.diverted_traffic_amount > 0:
                self.reroute_traffic(action_object)

        self.loss_forced_benign_traffic_drop = (self.benign_traffic_drop/global_settings.GB_to_KB)*global_settings.BENIGN_DROP_LOSS
        self.loss_delayed_benign_traffic = (self.benign_traffic_delay/global_settings.GB_to_KB)*global_settings.BENIGN_DELAY_LOSS
        # print('%s --> %s' % (self.loss_forced_benign_traffic_drop, self.loss_delayed_benign_traffic))

        current_obsv = None
        self.attack_mode()
        prev_traffic_drop = self.automated_traffic_drop
        current_traffic_amount = sum(global_settings.traffic_dist_risk_scores)
        self.automated_traffic_drop = max(current_traffic_amount - global_settings.RESOURCE_BANDWIDTH, 0)
        # print('Drop %s from %s'%(self.automated_traffic_drop,current_traffic_amount))
        if self.automated_traffic_drop <= 0:
            util_level = current_traffic_amount / global_settings.RESOURCE_BANDWIDTH
            # print("Link Utilization Level %s" % (util_level), end='')
            for j,lu in enumerate(global_settings.link_utilization):
                if util_level <= lu:
                    current_obsv = j
                    break
        else:
            util_level = self.automated_traffic_drop / current_traffic_amount
            # print("Packet Drop Level %s" % (util_level), end='')
            for j,lu in enumerate(global_settings.Drop_ratio):
                if util_level <= lu or j==len(global_settings.Drop_ratio)-1:
                    current_obsv = len(global_settings.link_utilization) + j
                    break
        # print("Current Observation %s"%(current_obsv))
        # print(global_settings.traffic_dist_risk_scores)
        # print("Traffic Drop %s --> Obsv ID %s"%(self.automated_traffic_drop,current_obsv))
        reward = ((prev_traffic_drop-self.automated_traffic_drop)/global_settings.GB_to_KB)*global_settings.BENIGN_DROP_LOSS\
                 -self.loss_forced_benign_traffic_drop-self.loss_delayed_benign_traffic
        reward /= global_settings.AVG_REWARD
        # print("Reward %s"%(reward))
        done = False
        if self.ob%global_settings.SAVE_RESULT_FREQ_DDoS==0:
            done = True
        return current_obsv,reward,done,{}