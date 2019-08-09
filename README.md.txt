# Pittsburgh Intersection Threat Assessment System (PITAS)
## an automated inspection system 

<br />

### Introduction:
Despite innovations in automotive safety features and traffic control systems, automotive collisions remain one of the most costly and dangerous problems in the United States. Intersections are particularly dangerous and are where over 40% of traffic collisions occur. In my project, **Pittsburgh Intersection Threat Assessment System (PITAS)**, I propose using city data on traffic collisions, intersection safety features, and intersection geometry to predict the number of collisions that will occur at all intersections of a city, determine which features contribute the most to each intersection’s safety rating, and allow city planners to interact with the model. **PITAS could be productized as a municipal decision assistance tool or a tool to help insurance companies set premiums.**

<br />

### Inputs:

**PITAS** recieves inputs from several disparate datasets:

- Road centerline shapes, road names, speed limits, one way status ([link](https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=1224))
- Traffic Sign descriptions and locations ([link](https://data.wprdc.org/dataset/city-traffic-signs))
- Traffic Light descriptions and locations ([link](https://data.wprdc.org/dataset/city-of-pittsburgh-signalized-intersections))
- Detailed accident descriptions including locations ([link](https://data.wprdc.org/dataset/allegheny-county-crash-data))
- Zoning information ([link](https://data.wprdc.org/dataset/zoning1))
- 311 Complaint information ([link](https://data.wprdc.org/dataset/311-data))

The ultimate input will combine this information as the following features:

<br />

### Model:
The inputs are fed into a Random Forest Multilabel Classification Model with 3 possible Risk Levels / labels:

1: 0 Accidents Per Year
2: 0-2 Accidents Per Year
3: >2 Accidents Per Year

This values are generated for each intersection, which serves as the output of the model.

<br />

### Interactivity:

**PITAS** is hosted at [pitas.herokuapp.com](pitas.herokuapp.com). At the site, you can toggle different features of a particular intersection to see how this could affect the Risk Level. 