from fastapi import FastAPI
import joblib
import pandas as pd
import requests

app = FastAPI()

# تحميل النموذج
model = joblib.load('traffic_model.pkl')

@app.get("/")
def read_root():
    return {"message": "Traffic AI API with OpenStreetMap is active!"}

def get_osm_data(lat, lon):
    # إرسال استعلام إلى Overpass API لجلب بيانات الطريق المحيط بالإحداثيات (بقطر 50 متر)
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    way(around:50,{lat},{lon})["highway"];
    out tags;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    # استخراج البيانات (في حال عدم وجود بيانات، نستخدم قيم افتراضية)
    tags = data['elements'][0]['tags'] if data['elements'] else {}
    
    # تحويل البيانات إلى تنسيق يفهمه النموذج
    lanes = int(tags.get('lanes', 2))
    maxspeed = int(tags.get('maxspeed', 60))
    length = 500  # طول ثابت للمقطع
    highway_encoded = 1 if tags.get('highway') in ['primary', 'motorway'] else 0
    
    return [length, lanes, maxspeed, highway_encoded]

@app.get("/predict-by-location")
def predict_by_location(lat: float, lon: float, hour: int):
    # 1. جلب البيانات من الخريطة
    road_features = get_osm_data(lat, lon)
    
    # 2. إضافة الوقت
    road_features.append(hour)
    
    # 3. تحضير البيانات للنموذج
    df = pd.DataFrame([road_features], 
                      columns=['length', 'lanes', 'maxspeed', 'highway_encoded', 'hour'])
    
    # 4. التنبؤ
    prediction = model.predict(df)
    
    return {
        "status": "success",
        "traffic_level": prediction[0],
        "debug_info": {"lat": lat, "lon": lon, "features": road_features}
    }