#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

@author: MinBin

"""

# import package
import random
import time
import logging
import itertools

import pylab as pl

logger = logging.getLogger("Ant Colony Optimisation")
logger.basicConfig = logging.basicConfig(level=logging.DEBUG)

############################################################
### max-min ant System (MMAS) ###

class MMAS(object):
    
    # parameter setting
    def __init__(self, num_iters, num_ants, init_alpha, alpha, beta, rho, q, 
                 place_dict,dist_dict):
        """
        num_iters: number of iterations (generations)
        num_ants: number of explorers (population/solutions)
        alpha: relative importance of pheromone
        beta: relative importance of heuristic information
        rho: pheromone residual coefficient
        q: pheromone intensity
        places_info: type + number + geocode
        """
        self.num_iters = num_iters
        self.num_ants = num_ants
        self.init_alpha = init_alpha
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        
        self.place_dict = place_dict
        self.dist_dict = dist_dict

        self.num_places = len(place_dict)
        self.place_names = place_dict.keys() # only type+number
        self.shortest = float('inf') # inital shortest distance (inf)
        self.ant_list = []
        
        pl.show()
        
    # problem construction
    def addPlace(self):
        #  create an empty dictionary for storing pheromones
        self.pheromones = dict.fromkeys(self.place_names, {})
        for key in self.pheromones.keys():
            self.pheromones[key] = dict.fromkeys(self.place_names, 0)
            
        #  create an empty dictionary for storing pheromone_deltas
        self.pheromone_deltas = dict.fromkeys(self.place_names, {})
        for key in self.pheromones.keys():
            self.pheromone_deltas[key] = dict.fromkeys(self.place_names, 0)
        
        # create an empty list to store best tour (route) 
        self.BestTour =  [None] * self.num_places
        
    def PutAnts(self):
        del self.ant_list [:] # same as clear()
        for a in range(self.num_ants):
            # randomly select a destination
            place = random.choice(self.place_names)
            ant = ANT(place, self.place_names,  self.dist_dict, self.pheromones)
            self.ant_list.append(ant)
    
    # define the searching method  
    def Search(self):
        for iteration in range(self.num_iters):
            
            start = time.time()
            
            self.PutAnts()
            tmpLen = float('inf') # for checking feasibility
            tmpTour = []
            
            for ant in self.ant_list:
                for t in range(self.num_places):
                    ant.MoveToNextPlace(self.alpha, self.beta)
                ant.local_search() # same as two_opt_search
                ant.UpdatePathLen()
                if ant.currLen < tmpLen:
                    self.bestAnt = ant
                    tmpLen = ant.currLen
                    tmpTour = ant.TabuList # TabuList records every solution that have been visited
            if tmpLen < self.shortest: # current distance < inital predefined shortest distance
                self.shortest = tmpLen # replace it with current one
                self.BestTour = tmpTour
                            
            self.UpdatePheromoneTrail() # update information
            end = time.time()
            
            logger.info("time: %d, iter: %d, shortest: %d, best: %s", 
                        end - start,iteration, self.shortest, self.BestTour)
            
            # plotting
            points = []
            for p in self.BestTour:
                if p:
                    points.append(self.place_dict[p])
# should plot it on map (needed to be revised)
            pl.plot(points)
            pl.scatter(points, s=30, c='r')
            pl.pause(0.01)

    def UpdatePheromoneTrail(self):
        ant = self.bestAnt
        updated_pheromone = self.q/ant.currLen # 1/Lk
        tabu =  ant.TabuList
        
        for Place, nextPlace in zip(tabu[:-1], tabu[1:]): # exclude (i,i)
            self.pheromone_deltas[Place][nextPlace] = updated_pheromone
            self.pheromone_deltas[nextPlace][Place] = updated_pheromone
        
        lastPlace = tabu[-1]
        firstPlace = tabu[0]
        self.pheromone_deltas[lastPlace][firstPlace] = updated_pheromone
        self.pheromone_deltas[firstPlace][lastPlace] = updated_pheromone
        
        for p1 in self.place_names:
            for p2 in self.place_names:
                if p1 != p2:
                    self.pheromones[p1][p2] = ((1 - self.rho) * self.pheromones[p1][p2] 
                    + self.pheromone_deltas[p1][p2])
                    if self.pheromones[p1][p2] < 0.001:
                        self.pheromones[p1][p2] = 0.001
                    if self.pheromones[p1][p2] > 10:
                        raise(Exception('too big Ph'))
                        self.pheromones[p1][p2] = 10
                    self.pheromone_deltas[p1][p2] = 0
                    
############################################################
### the behaviour of ants ###   
                    
class ANT(object):
     def __init__(self, currPlace, place_names, dist_dict, pheromones):
         self.currPlace = currPlace
         self.dist_dict = dist_dict
         self.pheromones = pheromones

         self.TabuList = [currPlace,]
         self.avl_places = list(set(place_names)) # avaliable places 
         self.avl_places.remove(currPlace)
         self.currLen = 0
         
     def SelectNextPlace(self, alpha, beta):
         # no avaliblae destination
         if len(self.avl_places) == 0:
             return None
         
         # get 16 closest locations
         near = itertools.islice(self.dist_dict[self.currPlace].keys(), 16)
         good_locs = [n for n in near if n in self.avl_places]
         if good_locs:
             sum_prob = 0
             self.transfer_prob_list = [] # selection probability for each place
             for location in self.avl_places:
                 sum_prob = sum_prob +(pow(self.pheromones[self.currPlace][location], alpha) *
                 pow(1.0/self.dist_dict[self.currPlace][location], beta))
                 transfer_prob = sum_prob
                 self.transfer_prob_list.append((location, transfer_prob))
             
             # roulette wheel
             thred = sum_prob * random.random() 
             for location, prob in self.transfer_prob_list:
                 if thred <= prob:
                     return location
         else:
             not_near = itertools.islice(self.dist_dict[self.currPlace].keys(), 
                                         16,
                                         len(self.dist_dict[self.currPlace]))
             
             good_locs = [n for n in not_near if n in self.avl_places]
             if good_locs:
                 return good_locs[0]
                 
     def MoveToNextPlace(self, alpha, beta):
         
         nextPlace = self.SelectNextPlace(alpha, beta)
         # exclude current place for monving to next step
         if nextPlace is not None:
             self.currPlace = nextPlace
             self.TabuList.append(nextPlace)
             self.avl_places.remove(nextPlace)
             
     def UpdatePathLen(self):
         for Place, nextPlace in zip(self.TabuList[:-1], self.TabuList[1:]):
             self.currLen = self.currLen + self.dist_dict[Place][nextPlace]
         
         lastPlace = self.TabuList[-1]
         firstPlace = self.TabuList[0]
         self.currLen = self.currLen + self.dist_dict[lastPlace][firstPlace]
     
     # swape the sequence
     def local_search(self):
         num = len(self.TabuList)
         for i in range(num):
             for j in range(num - 1, i, -1):
                 currPlace1 = self.TabuList[i]
                 prePlace1 = self.TabuList[(i - 1) % num]
                 currPlace2 = self.TabuList[j]
                 nextPlace2 = self.TabuList[(j + 1) % num]
                 
                 currLen = self.dist_dict[prePlace1][currPlace1]
                 + self.dist_dict[currPlace2][nextPlace2]
                 
                 nextLen = self.dist_dict[prePlace1][
                    currPlace2] + self.dist_dict[currPlace1][nextPlace2]
                 
                 if nextLen < currLen:
                     tempList = self.TabuList[i:j + 1]
                     self.TabuList[i:j + 1] = tempList[::-1]                    
       