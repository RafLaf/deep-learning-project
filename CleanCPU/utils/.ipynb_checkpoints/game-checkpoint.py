import time
import gym
import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np
import sys
import os
import scipy.sparse as sc






#from network import initnet 
#net=initnet(0.9,dtype)
#----------------------
#REAAAAAAAAAAAAAAADMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
## 1)  First choose your dtype
## 2)  TO RUN THIS PROGRAM ALONE DECOMMENT THE  2 LINES BEFORE
## 3)  YOU WILL HAVE TO COMMENT THEM AGAIN TO RUN MAIN
#----------------------



def launch_scenarios(Wout,display=0):
    global dtype
    global show
    Wout=np.reshape(Wout,(3,1025))
    Wout=torch.from_numpy(Wout)
    Wout=typedevice(Wout,device)
    #Wout=Wout.to(dtype=torch.float64)
    reward_list=[]
    start_time = time.time()
    nbep=3
    max_reward=0
    
    net.r=torch.zeros(512)
    #env = gym.make('CarRacing-v0')
    for i_episode in range(nbep):
        net.r=torch.zeros(512)
        observation = env.reset()
        #env.viewer.close()
        reward_sum=0
        feature=torch.zeros(1025,dtype=torch.long)#.to(device=device)
        #feature=torch.zeros(1025,dtype=torch.float64).to(device=device)
        feature[-1]=1
        #feature=torch.from_numpy(np.array(1024))
        for t in range(5000000):
            if display==2:
                env.render('human')
            if display==1:
                if i_episode%3==0:
                    env.render('human')
            if display==0:
                pass
            Wout=Wout.to(dtype=torch.long)
            action=torch.clip(torch.matmul(Wout,feature),-1,1)
            #erf ou 2sigmoid-1 ou tanh 
            action=action.detach().cpu().numpy()
            
            #a1=max(min((np.sum(np.array(feature.detach().numpy())*Wout[0:1024])+Wout[1024]),1),-1)
            #a2=max(min((np.sum(np.array(feature.detach().numpy())*Wout[1025:2049])+Wout[2049]),1),-1)
            #a3=max(min((np.sum(np.array(feature.detach().numpy())*Wout[2050:3074])+Wout[3074]),1),-1)
            #action=[a1,a2,a3]
            observation, reward, done, info = env.step(action)
            obs=np.array(observation)
            obs=np.moveaxis(obs,[2],[0])
            obs=np.array([obs])
            obs=torch.from_numpy(obs)
            obs=typedevice(obs,device)
            feature[:-1]=net.RCstep(obs.float(),0.5,1e-6)
            #feature=net.RCstep(obs.float(),0.5,1e-6)
            reward_sum+=reward
            if done and t<998 and reward_sum > 900:
                print("Episode finished after {} timesteps".format(t+1))
                reward_sum+=50000000
                break
            if reward_sum > max_reward:
                max_reward = reward_sum
            elif max_reward-reward_sum > 15:
                reward_sum=reward_sum-(1000-t*0.1)
                break
        print("step number:",t)
        print("sum reward:",reward_sum)
        reward_list.append(reward_sum)
    return -sum(reward_list)/nbep    #CMA es minimzes

def typedevice(tensor,devi):
    return tensor.to(device=devi)


if __name__ == "__main__":
    dtype = torch.long
    #dtype = torch.cuda.FloatTensor
    device = torch.device('cpu')
    #device= 'cuda'
    launch_scenarios.dtype=dtype
    try:
        W=np.load('W.npy',allow_pickle=True)
        print('loaded W')
    except FileNotFoundError:
        Nr,D,rho=512,10,0.9
        print('not found creating W')
        W=sc.random(Nr,Nr,density=float(D/Nr))
        W=rho/max(abs(np.linalg.eigvals(W.A)))*W
        W=(2*W-(W!=0))
        W=W.A
        np.save('W.npy',W)
    env = gym.make('CarRacing-v0')
    #env = gym.wrappers.Monitor(env, "./vid", force=True)
    from network import initnet
    import network
    network.device=device
    net=initnet(0.9,dtype,W)
    launch_scenarios(np.random.random(3*1025))
