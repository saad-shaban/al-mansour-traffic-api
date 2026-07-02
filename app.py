import streamlit as st
import requests
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime

# Set page configuration for a professional look
st.set_page_config(page_title="Insiyab", page_icon="🚗")

st.title("🚗 Insiyab AI")
st.subheader("Real-time Congestion Predictor")

# 1. Get location and save to session state
# This triggers the browser's native location permission request
location = streamlit_geolocation()

if location and location['latitude'] is not None:
    st.session_state['lat'] = location['latitude']
    st.session_state['lon'] = location['longitude']
    st.success(f"Location Detected: {st.session_state['lat']:.4f}, {st.session_state['lon']:.4f}")
else:
    st.info("Waiting for location access... Please allow permission in your browser.")

# 2. Button logic
if st.button("Analyze Current Traffic"):
    if 'lat' in st.session_state:
        with st.spinner("Connecting to AI engine... (this may take a moment if the server is waking up)"):
            try:
                lat = st.session_state['lat']
                lon = st.session_state['lon']
                hour = datetime.now().hour  # Use actual current hour
                
                api_url = f"https://al-mansour-traffic-api.onrender.com/predict-by-location?lat={lat}&lon={lon}&hour={hour}"
                
                # Increased timeout to 60 seconds to allow Render free-tier to wake up
                response = requests.get(api_url, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    st.metric(label="Traffic Status", value=result['traffic_level'].upper())
                    
                    # Show the map
                    data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                    st.map(data, zoom=15)
                elif response.status_code == 503 or response.status_code == 504:
                    st.error("The AI engine is still waking up. Please wait 10 seconds and try clicking 'Analyze' again.")
                else:
                    st.error(f"Error: Unable to get prediction (Status {response.status_code})")
                    
            except requests.exceptions.Timeout:
                st.error("The request timed out. The server is taking too long to respond. Please try again.")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
    else:
        st.warning("Location not yet detected. Please wait a moment.")