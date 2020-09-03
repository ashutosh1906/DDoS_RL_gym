import os
import global_settings
from Entities import defense_action,observation,training_result
import random
from stable_baselines.common.policies import MlpPolicy,MlpLstmPolicy
from stable_baselines import PPO2,DDPG
import DDoS_env

from stable_baselines import results_plotter
import matplotlib.pyplot as plt
from stable_baselines.bench import Monitor


log_dir = '/'.join([os.path.dirname(os.path.abspath(__file__)),'logs/'])

def prepare_observation_space():
    ob_id = 0
    for lu in global_settings.link_utilization:
        global_settings.observation_space.append(observation.observation(obsv_id=ob_id,linkU=True,pLevel=lu))
        ob_id += 1

    for pd in global_settings.Drop_ratio:
        global_settings.observation_space.append(observation.observation(obsv_id=ob_id,pDrop=True,pLevel=pd))
        ob_id += 1

    for ob in global_settings.observation_space:
        ob.print_properties()

def prepare_defense_space():
    defense_id = 0
    defense_action.defense(defense_id=defense_id)
    defense_id += 1
    for limit_function_type in global_settings.limit_function_type:
        for limit_ratio in global_settings.defense_list_ratios:
            global_settings.defense_space.append(
                defense_action.defense(defense_id=defense_id,limit_ratio=limit_ratio,limit_type=limit_function_type))
            defense_id += 1
    global_settings.defense_space.append(defense_action.defense(defense_id=defense_id, limit_ratio=0.0,limit_type=-1))

    # for defense in global_settings.defense_space:
    #     defense.print_properties()

    for i in range(51):
        global_settings.traffic_dist_risk_scores.append(random.randint(1,100))

    for i in range(51,101):
        global_settings.traffic_dist_risk_scores.append(random.randint(10,200))

    global_settings.defense_space[5].print_properties()
    global_settings.defense_space[5].set_limited_traffic_amount(sum(global_settings.traffic_dist_risk_scores)/3)
    print("Total Traffic %s"%(sum(global_settings.traffic_dist_risk_scores)))

    global_settings.defense_space[8].print_properties()
    global_settings.defense_space[8].set_limited_traffic_amount(sum(global_settings.traffic_dist_risk_scores)/3)
    print("Total Traffic %s"%(sum(global_settings.traffic_dist_risk_scores)))

def start_the_game():
    cyber = DDoS_env.cyberEnv(defense_list=global_settings.defense_space,obsv_list=global_settings.observation_space)
    cyber = Monitor(cyber,log_dir)

    defense_agent_decision_model = PPO2(MlpPolicy,cyber,verbose=1,gamma=0.95,ent_coef=0.1)
    callback = training_result.SaveOnBestTrainingRewardCallback(check_freq=global_settings.SAVE_RESULT_FREQ_DDoS, log_dir=log_dir)
    defense_agent_decision_model.learn(total_timesteps=global_settings.TOTAL_TRAIN_STEPS,callback=callback)

    # # Evaluate the agent
    # print("Evaluating the agent")
    # from stable_baselines.common.evaluation import evaluate_policy
    # mean_reward, std_reward = evaluate_policy(defense_agent_decision_model, defense_agent_decision_model.get_env(), n_eval_episodes=2)
    # print("Mean Reward %s Std Reward %s"%(mean_reward,std_reward))

    ''' Plot the performance'''
    results_plotter.plot_results([log_dir], global_settings.TOTAL_TRAIN_STEPS, results_plotter.X_TIMESTEPS, "DDoS Reward Results")
    plt.show()

if __name__=='__main__':
    print("Welcome to the main function")
    prepare_defense_space()
    prepare_observation_space()
    # prepare_observation_space()
    start_the_game()




