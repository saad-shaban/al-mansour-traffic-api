import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

with st.spinner("Analyzing road data..."):
            try:
                hour = 12 
                api_url = f"https://al-mansour-traffic-api.onrender.com/predict-by-location?lat={lat}&lon={lon}&hour={hour}"
                response = requests.get(api_url, timeout=15) # Increased timeout
                
                if response.status_code == 200:
                    result = response.json()
                    st.metric(label="Traffic Status", value=result['traffic_level'].upper())
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")


# Set page configuration for a "Waze-like" professional look
st.set_page_config(page_title="Traffic Sentinel", page_icon="🚗")

st.title("🚗 Traffic Sentinel AI")
st.subheader("Real-time Congestion Predictor")

# 1. Automatic GPS Detection
st.write("Detecting your precise location...")
location = streamlit_geolocation()

if location and location['latitude'] is not None:
    lat, lon = location['latitude'], location['longitude']
    st.success(f"Location Detected: {lat:.4f}, {lon:.4f}")

    # 2. Automatically call the API
    if st.button("Analyze Current Traffic"):
        with st.spinner("Analyzing road data..."):
            try:
                # Hour is taken from current time
                hour = 12 
                api_url = f"https://al-mansour-traffic-api.onrender.com/predict-by-location?lat={lat}&lon={lon}&hour={hour}"
                response = requests.get(api_url).json()
                
                # 3. Professional Display
                traffic = response['traffic_level']
                st.metric(label="Traffic Status", value=traffic.upper())
                
                # Show the map
                data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(data, zoom=15)
                
            except Exception as e:
                st.error("Could not connect to the AI engine.")
else:
    st.info("Please allow location access to see traffic predictions.")
