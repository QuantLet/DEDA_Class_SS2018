# Using Ant Colony Optimisation for Logistic Route Planning: #
## A case for logistics distribution of 7-Eleven stores in Xinyi District, Taipei ##
----------
### Abstract ###
Taiwan is the second highest in the world for the ratio of convenience stores per population in 2017. According to Statistics Department of the Ministry of Economic Affairs (MOEA), there were 10,662 different convenience stores at the beginning of March 2017. In average, every 2,211 people around the country shares one convenience store. Convenience stores play an critical role in Taiwanese everyday life.
Having high variety and operating 24/7, frequent replenishment is required for the retailers in Taiwan. However, due to the high density of stores, the logistic networks for replenishment are relatively complex. In this project, we use the replenishment delivery of 7-Eleven stores in Xinyi District as an example and apply ant colony optimisation (ACO), which is a population-based evolutionary algorithm to plan the logistic route for minimising travel distance for delivery vehicles. The vehicles require to travel all over the stores (travelling salesman problem, TSP) and finally return to the warehouse, which is also the start point for the delivery. The store information (e.g., store id, address) is obtained from the 7-Elevn ibon website (https://www.ibon.com.tw) and the location of warehouse is assumed in the project. The traffic condition is not considered.

The distribution of 7-Eleven stores and warehouse:
<iframe src="https://cdn.rawgit.com/linminbin/DEDA_Class_SS2018/c3d4e0c8/Min-Bin%20Lin/Route%20Optimisation/xinyi_map/index.html" width="600" height="450" frameborder="0" style="border:0" allowfullscreen></iframe>
