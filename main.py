from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import requests

app = FastAPI()

# Load the trained model
# Ensure 'traffic_model.pkl' is in the same directory as this file
try:
    model = joblib.load('traffic_model.pkl')
except Exception as e:
    print(f"Error loading model: {e}")

@app.get("/")
def read_root():
    return {"message": "Traffic AI API is running and connected to OSM!"}

def get_osm_data(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    way(around:50,{lat},{lon})["highway"];
    out tags;
    """
    # Header is required by Overpass API to avoid 406 Not Acceptable errors
    headers = {'User-Agent': 'TrafficAI-Project/1.0'}
    
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if not data.get('elements'):
        return None
        
    return data['elements'][0]['tags']

@app.get("/predict-by-location")
def predict_by_location(lat: float, lon: float, hour: int):
    try:
        # 1. Fetch data from OpenStreetMap
        tags = get_osm_data(lat, lon)
        if not tags:
            raise HTTPException(status_code=404, detail="No road data found for this location.")
        
        # 2. Extract and clean features
        lanes = int(tags.get('lanes', 2))
        maxspeed_str = tags.get('maxspeed', '60')
        # Clean string to get only digits (e.g., '60 km/h' -> 60)
        maxspeed = int(''.join(filter(str.isdigit, maxspeed_str))) if maxspeed_str and any(char.isdigit() for char in maxspeed_str) else 60
        
        length = 500  # Default segment length
        highway_encoded = 1 if tags.get('highway') in ['primary', 'motorway', 'trunk'] else 0
        
        # 3. Prepare for prediction
        df = pd.DataFrame([[length, lanes, maxspeed, highway_encoded, hour]], 
                          columns=['length', 'lanes', 'maxspeed', 'highway_encoded', 'hour'])
        
        # 4. Predict
        prediction = model.predict(df)
        
        return {
            "status": "success",
            "traffic_level": str(prediction[0]),
            "metadata": {"lanes": lanes, "maxspeed": maxspeed, "highway_type": tags.get('highway')}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))