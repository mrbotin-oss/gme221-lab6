import geopandas as gpd 
import pandas as pd
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier 
from sklearn.metrics import accuracy_score

parcels = gpd.read_file("data/parcel.geojson") 
roads = gpd.read_file("data/roads.geojson") 
water = gpd.read_file("data/water_network.geojson") 
landuse = gpd.read_file("data/landuse.geojson") 
schools = gpd.read_file("data/schools.geojson") 
tourism = gpd.read_file("data/tourism.geojson") 

# print(parcels.head()) 
# print(parcels.crs)

roads = roads.to_crs(parcels.crs) 
water = water.to_crs(parcels.crs) 
landuse = landuse.to_crs(parcels.crs) 
schools = schools.to_crs(parcels.crs) 
tourism = tourism.to_crs(parcels.crs) 


# -------------Part C. Spatial Feature Engineering ------------------

parcels["area"] = parcels.geometry.area 

parcels["perimeter"] = parcels.geometry.length 

parcels["compactness"] = ( 
    parcels["area"] / 
    (parcels["perimeter"] ** 2) 
)

parcels["centroid"] = parcels.geometry.centroid 

# distance to road
parcels["dist_to_road"] = parcels["centroid"].apply( 
    lambda p: roads.distance(p).min() 
)

# distance to water network
parcels["dist_to_water"] = parcels["centroid"].apply( 
    lambda p: water.distance(p).min() 
) 

# distance to school
parcels["dist_to_school"] = parcels["centroid"].apply( 
    lambda p: schools.distance(p).min() 
)

# distance to tourism sites
parcels["dist_to_tourism"] = parcels["centroid"].apply( 
    lambda p: tourism.distance(p).min() 
)

# count of schools within 500m
print("Calculating school counts within 500m...")
buffer_500m = parcels["centroid"].buffer(500)

# spatial join between 500m buffers and schools
joined_schools = gpd.sjoin(
    gpd.GeoDataFrame(geometry=buffer_500m, crs=parcels.crs), 
    schools, 
    how="left", 
    predicate="contains"
)

# count schools per parcel index
parcels["schools_within_500m"] = joined_schools.groupby(joined_schools.index).size() - joined_schools.groupby(joined_schools.index)['index_right'].apply(lambda x: x.isna().sum())

# tourism density (Count within 1km) 
print("Calculating tourism density within 1km...")
buffer_1km = parcels["centroid"].buffer(1000)
joined_tourism = gpd.sjoin(
    gpd.GeoDataFrame(geometry=buffer_1km, crs=parcels.crs), 
    tourism, 
    how="left", 
    predicate="contains"
)
parcels["tourism_density_1km"] = joined_tourism.groupby(joined_tourism.index).size() - joined_tourism.groupby(joined_tourism.index)['index_right'].apply(lambda x: x.isna().sum())


# spatial join with land use
parcels_landuse = gpd.sjoin( 
    parcels, 
    landuse[["Name", "geometry"]], 
    how="left", 
    predicate="intersects" 
) 

# encode land use categories 
parcels_landuse["landuse_code"] = ( 
    parcels_landuse["Name"] 
    .astype("category") 
    .cat.codes 
) 

# print unique land use categories and their codes 
print( 
    parcels_landuse[ 
    ["Name", "landuse_code"] 
    ] 
    .drop_duplicates() 
    .sort_values("landuse_code") 
) 


# ------------- GeoAI Model Construction --------------------------------

# encode target variable (land use class) 
parcels_landuse["target_code"] = ( 
    parcels_landuse["ASS_CLASSI"] 
    .astype("category") 
    .cat.codes 
) 

features = [ 
    "area", 
    "perimeter", 
    "compactness", 
    "dist_to_road", 
    "dist_to_water", 
    "dist_to_school", 
    "dist_to_tourism",
    "schools_within_500m",
    "tourism_density_1km", 
    "landuse_code" 
] 

data = parcels_landuse.dropna( 
    subset=features + ["target_code"] 
) 

class_counts = data["target_code"].value_counts()
valid_classes = class_counts[class_counts >= 2].index
data = data[data["target_code"].isin(valid_classes)].copy()

X = data[features] 
y = data["target_code"] 


# ---------------------- Training and Testing Data ---------------------------

X_train, X_test, y_train, y_test = train_test_split( 
    X, 
    y, 
    test_size=0.30, 
    random_state=42
)

# classifier 1: Random Forest 
rf_model = RandomForestClassifier(n_estimators=100, random_state=42) 
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test) 
rf_accuracy = accuracy_score(y_test, rf_pred) 

# classifier 2: Gradient Boosting (HistGradientBoosting)
gb_model = HistGradientBoostingClassifier(random_state=42)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)
gb_accuracy = accuracy_score(y_test, gb_pred)

# compare model performance 
print("\n" + "="*40)
print("      MODEL PERFORMANCE COMPARISON      ")
print("="*40)
print(f"Random Forest Accuracy:        {rf_accuracy:.4f}")
print(f"Gradient Boosting Accuracy:   {gb_accuracy:.4f}")
print("="*40)

# select the best performing model automatically
if gb_accuracy > rf_accuracy:
    best_model = gb_model
    print("Selecting Gradient Boosting for spatial mapping output.")
else:
    best_model = rf_model
    print("Selecting Random Forest for spatial mapping output.")


# ---------------------- Apply Predictions to Spatial Data ----------------------------

data["predicted_class"] = best_model.predict(X) 

categories = ( 
    data["ASS_CLASSI"] 
    .astype("category") 
    .cat.categories 
) 

data["predicted_label"] = data["predicted_class"].apply( 
    lambda code: categories[code] if code < len(categories) else "Unknown"
) 

data["correct_prediction"] = ( 
    data["ASS_CLASSI"] == 
    data["predicted_label"] 
) 

print("\nSample Predictions:")
print( 
    data[ 
        [ 
            "ASS_CLASSI",
            "predicted_label", 
            "correct_prediction" 
        ] 
    ].head() 
)

# --------------------- Export GeoAI Result ----------------------------------

data = data.drop( 
    columns=["centroid"], 
    errors="ignore" 
) 

# export to geojson 
data.to_file( 
    "output/parcel_geoai_prediction.geojson", 
    driver="GeoJSON" 
) 

print("GeoAI output exported.") 