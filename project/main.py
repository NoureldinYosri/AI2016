import gym
from random import random,shuffle,choice;
import numpy as np;
from math import exp;
import logger;

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

def mutate(x):
	w = [v for v in x];
	mutation_strenght = 1
	for i in xrange(6):
		w[i] = np.array(w[i]) + mutation_strenght * (1-2*np.array(128));
		if sum(w[i]) : w[i] = w[i] / (sum(w[i]) + 0.0);
	return w ;

def mate(w1,w2,fit1,fit2):
	if fit1 + fit2 == 0: return w1,w2;
	w1 = np.array(w1);
	w2 = np.array(w2);
	p = fit1/(fit1 + fit2 + 0.0);
	return p*w1 + (1 - p)*w2,(1 - p)*w1 + p*w2;

def sort_by_fitness(population,fitness):
	aux = [[fitness[i],i] for i in xrange(len(population))];
	aux.sort();
	aux.reverse();
	return [population[x[1]] for x in aux];

def create_population(n):
	ret = [];
	for i in xrange(n):
		gene = [];
		for j in xrange(6):
			aux = np.random.rand(128);
			if sum(aux): aux = aux / (sum(aux) + 0.0);
			gene.append(aux);
		ret.append(gene);
	return ret;

def evolve():
	env.monitor.start('experiment',force = True)
	num_episodes = 50;
	pop_size = 50;
	pairing = 10;
	new_blood = 3;
	old_mutate = 2;
	population = create_population(pop_size)
	best = 0;
	for _ in xrange(num_episodes):
		print "start new episode"
		fitness = [run_episode(w) for w in population];
		children = [];
		for i in xrange(pairing):
			X = choice(range(pop_size));
			Y = choice(range(pop_size));
			X,Y = mate(population[X],population[Y],fitness[X],fitness[Y])
			children.append(mutate(X));
			children.append(mutate(Y));
		population = sort_by_fitness(population,fitness);
		population = population[:-(pairing + new_blood + old_mutate)];
		population = population + children + create_population(new_blood) + [mutate(choice(population)) for i in xrange(old_mutate)];
		print "done with %d episodes ,max = %d"%(_ + 1,max(fitness));
		logger.write("done with %d episodes ,max = %d\n"%(_ + 1,max(fitness)));
		if max(fitness) > best: 
			best = max(fitness)
			logger.save(population[0],"genetic algorithms ... new max = %d\n"%best)

	env.monitor.close()

evolve();
