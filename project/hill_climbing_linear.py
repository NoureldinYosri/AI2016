import gym
from random import random,choice;
import numpy as np;

env = gym.make('AirRaid-ram-v0')
env.monitor.start('hill_climbing_linear',force = False)

def get_action(x,W):
	x = np.array(x);
	#x = x/(sum(x) + 0.0);
	val = [np.dot(x,w) for w in W];
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


num_episodes = 100;
W = [np.random.rand(128) for i in xrange(6)];
score = [];
best = 0;
alpha = 100
for _ in xrange(num_episodes):
	new_W = np.array(W) + alpha * np.array([np.random.rand(128) for i in xrange(6)]);
	f = run_episode(new_W)
	if f > best:
		best = f;
		W = new_W;
		alpha /= 2.0;
		alpha = max(alpha,0.1)

	score.append(f);
	print "done with %d episodes ,score = %d"%(_ + 1,f);
"""	if len(score) == 101: score.pop(0);
	if len(score) == 100 and sum(score) / 100 >= 195:
		print "solved after %d episodes"%(_ - 99)
		print "first 10 : ",score[:10],"\nlast 10 : ",score[90:]
		break;
	"""

print "final score = ",run_episode(W,True);
env.monitor.close()
