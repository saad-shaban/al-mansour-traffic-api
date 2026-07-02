import streamlit as st
import requests
import pandas as pd

st.title("Traffic AI Navigator")

# 1. Get user location (Streamlit has a browser-based location feature)
if st.button("Check Traffic at My Location"):
    # This is a placeholder for actual browser GPS fetching
    lat, lon = 33.3152, 44.3661 
    hour = 8
    
    # 2. Call your existing API
    url = f"https://al-mansour-traffic-api.onrender.com/predict-by-location?lat={lat}&lon={lon}&hour={hour}"
    response = requests.get(url).json()
    
    # 3. Display result
    traffic = response['traffic_level']
    st.write(f"Current Traffic Level: **{traffic}**")
    
    # 4. Show on map
    data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(data)