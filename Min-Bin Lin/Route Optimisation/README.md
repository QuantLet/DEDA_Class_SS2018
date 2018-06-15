# Using Ant Colony Optimisation for Logistic Route Planning: #
## A Case for Logistic Distribution of 7-Eleven Stores in the Xinyi District of Taipei ##
----------
### Introduction ###
<span style="color:black">
Taiwan is the second highest in the world for the ratio of convenience stores per population in 2017. According to Statistics Department of the Ministry of Economic Affairs (MOEA), there were 10,662 different convenience stores at the beginning of March 2017. In average, every 2,211 people around the country shares one convenience store. Convenience stores play an critical role in Taiwanese everyday life.
Having high variety and operating 24/7, frequent replenishment is required for the retailers in Taiwan. However, due to the high density of stores, the logistic networks for replenishment are relatively complex. In this project, we use the replenishment delivery of 7-Eleven stores in the Xinyi District as an example and apply ant colony optimisation (ACO), which is a population-based evolutionary algorithm to plan the logistic route for minimising travel distance for delivery vehicles. The vehicles require to travel all over the stores (travelling salesman problem, TSP) and finally return to the warehouse, which is also the start point for the delivery. The store information (e.g., store id, address) is obtained from the [7-Eleven ibon website](https://www.ibon.com.tw) and the location of warehouse is assumed in the project. The traffic condition is not considered.
</span>

<span style="color:black">
There are 63 7-Eleven stores and a warehouse in the Xinyi District. The distribution of 7-Eleven stores and warehouse (plotted by [folium package](http://folium.readthedocs.io/en/latest/)):
</span>

[Xinyi District Map](https://cdn.rawgit.com/linminbin/DEDA_Class_SS2018/c3d4e0c8/Min-Bin%20Lin/Route%20Optimisation/xinyi_map/index.html)

### 1. Research Process ###

![](pic/research process.png)

### 2. Data Collection and Distance Calculation ###

**File:**
<span style="color:blue">
*DataCollection_route_optimisation.py*
</span>

#### 2.1 Data Collection ####
<span style="color:black">
There are two set of data: warehouse and shop. Each data entry has six elements: name, address, entry_id, entry_type (warehouse or shop), latitude(lat), and longitude(lon). This information is stored in the dictionary. Below is an example for representation of data entry:
</span>

- warehouse 0 (倉庫) at address 台北市忠孝東路四段560號 (25.0407381, 121.5637989)

<span style="color:black">
The warehouse location is assumed as "台北市忠孝東路四段560號" and store data is scrapped from the 7-Eleven website by requests.post with url_data "strTargetField" and "strKeyWords" to specify requested data.
</span>

#### 2.2 Distance Calculation ####
<span style="color:black">
Before distance calculation, we need to convert all of addresses into geocodes, which include latitude and longitude in order to  represent the location accurately and plot maps. The geocoding and distance calculation are computed by [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start?hl=zh-tw) and [Google Maps Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/intro?hl=zh-tw), respectively. The Google Maps API only allow  2,500 free requests per day in total. To avoid over-requesting data, we use [Dill package ](https://pypi.org/project/dill/) to pickle the data.
</span>

### 3. Problem Assumption ###
- <span style="color:black">The delivery has to travel all over the stores in the Xinyi District and then return to the start place (warehouse).</span>

- <span style="color:black">The traffic condition is not considered.</span>

- <span style="color:black">The types of delivery vehicles and gasoline consumption are not considered.</span>

### 4. Problem Formulation ###
