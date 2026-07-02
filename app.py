import streamlit as st
import requests
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Insiyab", page_icon="🚗")

st.title("🚗 Insiyab AI")

# 1. Get location and save to session state
location = streamlit_geolocation()

if location and location['latitude'] is not None:
    # Save to session state so it persists
    st.session_state['lat'] = location['latitude']
    st.session_state['lon'] = location['longitude']
    
    st.success(f"Location Detected: {st.session_state['lat']:.4f}, {st.session_state['lon']:.4f}")

# 2. Button logic
if st.button("Analyze Current Traffic"):
    # Check if we have the location stored in memory
    if 'lat' in st.session_state:
        with st.spinner("Analyzing road data..."):
            try:
                lat = st.session_state['lat']
                lon = st.session_state['lon']
                hour = 12 
                
                api_url = f"https://al-mansour-traffic-api.onrender.com/predict-by-location?lat={lat}&lon={lon}&hour={hour}"
                response = requests.get(api_url, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    st.metric(label="Traffic Status", value=result['traffic_level'].upper())
                    
                    # Show the map
                    data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                    st.map(data, zoom=15)
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
    else:
        st.warning("Please wait for location detection first.")
