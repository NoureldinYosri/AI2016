import gym
from random import random;
import numpy as np;
from math import exp;

env = gym.make('AirRaid-ram-v0')

def g(z):
	return 1.0/(1 + exp(-z));

def get_action(x,W):
	x = np.array(x);
	x = x/(sum(x) + 0.0)
	val = [np.dot(x,w) for w in W];
	val = [g(z) for z in val];
	return val.index(max(val));

def run_episode(W,show = False):
	f = 0;
	observation = env.reset()
	while True:
	    if show: env.render()
	    action = get_action(observation,W);
	    observation, reward, done, info = env.step(action) 
	    f += reward;
	    #if(show): print reward
	    if done : break;
	return f;

num_episodes = 50;
W = [np.random.rand(128) for i in xrange(6)];
alpha = 10;
score = [];
best = 0;
for _ in xrange(num_episodes):
	noise = np.array([np.random.rand(128) for i in xrange(6)]);
	new_W = np.array(W) + noise * alpha;
	
	f = run_episode(new_W)
	if f > best:
		best = f;
		W = new_W
		noise /= 2.0;
		alpha = max(alpha,1e-1)
	score.append(f);
	print "done with %d episodes ,score = %d"%(_ + 1,f);
"""	if len(score) == 101: score.pop(0);
	if len(score) == 100 and sum(score) / 100 >= 195:
		print "solved after %d episodes"%(_ - 99)
		print "first 10 : ",score[:10],"\nlast 10 : ",score[90:]
		break;
	"""

#print sum(score)/100;
run_episode(W,True);
print best;