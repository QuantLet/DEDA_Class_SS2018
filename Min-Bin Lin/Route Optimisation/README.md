# Using Ant Colony Optimisation for Logistic Route Planning: #
## A Case for Logistic Distribution of 7-Eleven Stores in the Xinyi District of Taipei ##
----------
### Introduction ###
Taiwan is the second highest in the world for the ratio of convenience stores per population in 2017. According to Statistics Department of the Ministry of Economic Affairs (MOEA), there were 10,662 different convenience stores at the beginning of March 2017. In average, every 2,211 people around the country shares one convenience store. Convenience stores play an critical role in Taiwanese everyday life.
Having high variety and operating 24/7, frequent replenishment is required for the retailers in Taiwan. However, due to the high density of stores, the logistic networks for replenishment are relatively complex. In this project, we use the replenishment delivery of 7-Eleven stores in the Xinyi District as an example and apply ant colony optimisation (ACO), which is a population-based evolutionary algorithm to plan the logistic route for minimising travel distance for delivery vehicles. The vehicles require to travel all over the stores (travelling salesman problem, TSP) and finally return to the warehouse, which is also the start point for the delivery. The store information (e.g., store id, address) is obtained from the [7-Eleven ibon website](https://www.ibon.com.tw) and the location of warehouse is assumed in the project. The traffic condition is not considered.

There are 63 7-Eleven stores and a warehouse in the Xinyi District. The distribution of 7-Eleven stores and warehouse (plotted by [folium package](http://folium.readthedocs.io/en/latest/)):

[Xinyi District Map](https://cdn.rawgit.com/linminbin/DEDA_Class_SS2018/c3d4e0c8/Min-Bin%20Lin/Route%20Optimisation/xinyi_map/index.html)

### 1. Research Process ###

![](pic/research.png)

<p style="text-align: center;">
Figure 1-1 Research flow
</p>

### 2. Data Collection and Distance Calculation ###

**File:**
*DataCollection_route_optimisation.py*

#### 2.1 Data Collection ####
There are two set of data: warehouse and shop. Each data entry has six elements: name, address, entry_id, entry_type (warehouse or shop), latitude(lat), and longitude(lon). This information is stored in the dictionary. Below is an example for representation of data entry:

- warehouse 0 (倉庫) at address 台北市忠孝東路四段560號 (25.0407381, 121.5637989)

The warehouse location is assumed as "台北市忠孝東路四段560號" and store data is scrapped from the 7-Eleven website by requests.post with url_data "strTargetField" and "strKeyWords" to specify requested data.

#### 2.2 Distance Calculation ####
Before distance calculation, we need to convert all of addresses into geocodes, which include latitude and longitude in order to  represent the location accurately and plot maps. The geocoding and distance calculation are computed by [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start?hl=zh-tw) and [Google Maps Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/intro?hl=zh-tw), respectively. The Google Maps API only allow  2,500 free requests per day in total. To avoid over-requesting data, we use [Dill package ](https://pypi.org/project/dill/) to pickle the data.

### 3. Problem Assumption ###
- The delivery has to travel all over the stores in the Xinyi District and then return to the start place (warehouse).

- The traffic condition is not considered.</span>

- The types of delivery vehicles and gasoline consumption are not considered.

### 4. Problem Formulation ###
The problem (TSP) is formulated as below:

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/svgs/859dd0499d602687f9c141d045454ad1.svg?invert_in_darkmode" align=middle width=358.25626485pt height=47.5115553pt/></p>

subject to

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/svgs/46883a4fb678d10d068bf9a1b40979e1.svg?invert_in_darkmode" align=middle width=371.771763pt height=47.5115553pt/></p>

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/svgs/8adf0213d561dc9e98f8f5a4b8ba002b.svg?invert_in_darkmode" align=middle width=371.1781788pt height=47.5115553pt/></p>

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/svgs/bbea2cf60526cf83c9907b1824b1e370.svg?invert_in_darkmode" align=middle width=394.70914065pt height=17.0319402pt/></p>

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/svgs/d88243e88a0ff3f40d846c69e619e4f7.svg?invert_in_darkmode" align=middle width=358.3680606pt height=17.0319402pt/></p>

where \(d_{ij}\)  represent the actual distance from  location \(i\) to location \(j\). \(x_{ij}\) is a dummy variable. If \(x_{ij}=1\), the path goes from  location \(i\) to location \(j\); otherwise, the path does not go from location \(i\) to location \(j\). \(u_{i}\) and \(u_{j}\) are the sequence number of  location \(i\) and location \(j\) in the tour, respectively.

The equation (1) is the sum of the distance for the delivery route that travels from location 1 (warehouse) to all the stores. The equation (2) and equation (3) limit that the travel from location \(i\) to location \(j\) can only have "one ending location" and "one starting location." The equation (3) proves that every feasible solution contains only one closed sequence of locations,  it suffices to show that every subtour in a feasible solution passes through location 1. The equation (5) is the Miller-Tucker-Zemlin (MTZ) constraint, which eliminates the subtours.

### 5. Route Optimisation ###
#### 5.1 Ant Colony Optimisation (ACO) ####

**File:**
*ACO_route_optimisation.py*

ACO was initially proposed by  Marco Dorigo (1992). It is a metaheuristic algorithm for finding optimal paths, based on the simulation of the foraging behaviour of a colony of searching ants. After an ant finds food, it generates pheromones on the way back to the nest to inform other ants of the path to the food. The pheromones fade over time and the unused paths become less likely to be taken; otherwise, the density of pheromones on the used paths becomes higher.

![](pic/ant.png)
<p style="text-align: center;">
Figure 5-1 Shortest path find by an ant colony
</p>
<p style="text-align: center;">
Source: Johann Dréo (https://commons.wikimedia.org/wiki/File:Aco_branches.svg)
</p>


In this project, we implement the Max-Min Ant System (MMAS) (Stützle and Hoos, 1996), which we only update pheromones by
for \(\Delta\tau_{ij} = q/d_{BestTour}\) the best ant at the iteration (\(q\) controls the degree of influence of \(\Delta\tau_{ij}\)). If the path is unused, the the density of pheromones is decreased by \(\rho\) (a given initial parameter).  

Additionally, the selection of next place is based on the probability constructed by the pheromones. The probability of ant  \(k\) at location \(i\) chooses to go to location \(j\) is as follows:

<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/None/svgs/e1c266efd778e39f0e575dcfca83e753.svg?invert_in_darkmode" align=middle width=169.52870055pt height=42.92819685pt/></p>
<p align="center"><img src="https://rawgit.com/linminbin/DEDA_Class_SS2018/None/svgs/a2ff07f6cfd19f84cc40b4bdfaa7454b.svg?invert_in_darkmode" align=middle width=77.40686415pt height=22.70986245pt/></p>

where \(\alpha\) and \(\beta\) determines
pheromone trail and the heuristic information; \(\tau_{ij}\) and \(\eta_{ij}\) are the pheromone trail and the locally available heuristic information, respectively. \(X_i\) are all  the feasible (visitable) locations of ant 􏰯\(k\).

The local search tries to swap the sequence of the tour at various points (e.g., 1-2-3-4 to 3-4-2-1.) to determine if a different sequence can generate better fitness values (shorter distance).

![](pic/ACO.png)
<p style="text-align: center;">
Figure 5-2 The process of ant colony optimisation
</p>

#### 5.2 Application and Result ####
**File:**
*Application_route_optimisation.py* (main execution file)

The parameter setting for the project: (based on the literature):


- Initial place (init_place) = 'warehouse 0'
- Number iterations (num_iters) = 2,000
- Number of ants (num_ants) = 50 (also called population)
- Initial  \(\alpha\)  (init_alpha) = 10
- \(\alpha\) (alpha) = 1
- \(\beta\) (beta) = 3
- \(\rho\) (rho) = 0.3
- \(q\) = 80

The optimised route distance is 40,307 m. The optimisation process of ACO is shown as below:
![](pic/optimisation.png)
<p style="text-align: center;">
Figure 5-3 Optimisation process
</p>

The final logistic route is demonstrated by the map (plotted by [folium package](http://folium.readthedocs.io/en/latest/)):

[Route Map](https://cdn.rawgit.com/linminbin/DEDA_Class_SS2018/07a1a29c/Min-Bin%20Lin/Route%20Optimisation/index.html)




### 6. Literature Review ###

- Blum, C. (2005). Ant colony optimization: Introduction and recent trends. Physics of Life reviews, 2(4), 353-373.
- Le, T. Q., & Pishva, D. (2015, July). Optimization of convenience stores' distribution system with web scraping and Google API service. In Advanced Communication Technology (ICACT), 2015 17th International Conference on (pp. 596-606). IEEE.
- Stützle, T., & Hoos, H. H. (2000). MAX–MIN ant system. Future generation computer systems, 16(8), 889-914.
- Wikipedia: Ant colony optimization algorithms. FL: Wikimedia Foundation, Inc. Retrieved June 16, 2018, from https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms.
