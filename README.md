# GmE 221 – Laboratory Exercise 6: GeoAI: Spatial Prediction Using Parcel-Based Feature Engineering 

# Overview
- This laboratory exercise performs descriptive GIS analysis, overlay analysis, spatial statistics, and raster-vector integration into Geo-AI based spatial prediction.

# Environment Setup
- Python
- PostgreSQl with PostGIS
- Geopandas, scikit-learn, matplotlib, QGIS, Github

# How to Run
1. Activate the virtual environment
2. Run the analysis.py to run the full spatial statistical analysis pipeline.

# Reflection

# Part B. Data Loading Reflection 
1. Parcels were used as the prediction unit because the goal is to predict parcel classifications based on their shape and location. Other prediction units could be used if the study had a different research goal.
2. In spatial analysis, roads are used to represent movement and access between locations. They help analyze connectivity, accessibility, travel routes, distances, transportation patterns, and the relationships between spatial features.
3. Tourism can affect parcel classification because tourist attractions attract many visitors, which can influence the development and land use of nearby areas. As a result, parcels near tourist destinations are more likely to be classified as commercial, mixed-use, or higher-density developments.
4. No machine learning has been performed at this stage, as the process has only involved loading the required datasets for analysis.

# Part C. Feature Engineering Reflection
5. Geometry cannot be used directly in machine learning because ML models require numerical inputs, while geometries are complex spatial objects. Instead, measurable geometric characteristics, such as area, perimeter, or shape metrics, are extracted and used as input features for the model.
6. Distances are meaningful features because they describe how close or far spatial objects are from one another. In spatial analysis, nearby locations often have stronger relationships and similar characteristics, so distance helps capture the influence of surrounding features and provides important spatial context for machine learning models.
7. I think distance to roads is the most influential feature because roads provide access and connectivity, which strongly affect how land is developed and used. Parcels that are closer to roads are more likely to have higher-density or commercial land-use classifications due to better accessibility and increased economic activity.

