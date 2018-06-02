#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

@author: MinBin

"""

# import packages        
import dill
from operator import itemgetter
from collections import OrderedDict

from ACO_route_optimisation import MMAS, ANT

# Pickle file names
DISTANCE_MATRIX_PKL = 'distance_matrix.pkl'
PLACE_INFO_PKL = 'place_info.pkl'
PLACE_NAMES_PKL = 'place_names.pkl'
PLACE_DICT_PKL = 'place_dict.pkl'

############################################################
# load required data

distance_matrix = dill.load(open(DISTANCE_MATRIX_PKL)) 
place_names = dill.load(open(PLACE_NAMES_PKL))
place_dict = dill.load(open(PLACE_DICT_PKL))

############################################################
# data processing
   
dist_zipped = zip(place_names, zip(*distance_matrix))
dist_dict = {}
for key, vals in dist_zipped:
    dist_dict[key] = {}
    for i, item in enumerate(vals):
        dist_dict[key][place_names[i]] = item
    
sorted_dist_dict = {}
# sort the distance dictionary by values
for key in dist_dict.keys():
    sorted_tuples = sorted(dist_dict[key].items(), key=itemgetter(1))
    ordered_subdict = OrderedDict(sorted_tuples)
    sorted_dist_dict[key] = ordered_subdict
        
dist_dict = sorted_dist_dict
 
############################################################       
# apply ACO

aco = MMAS(num_iters=3000, num_ants=50, init_alpha=10, alpha=1, beta=3, rho=0.3,
            q=80, place_dict=place_dict,dist_dict=dist_dict)

aco.addPlace()
aco.Search()    