from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import requests

app = FastAPI()

try:
    model = joblib.load('traffic_model.pkl')
except Exception as e:
    print(f"Error loading model: {e}")

@app.get("/predict-by-location")
def predict_by_location(lat: float, lon: float, hour: int):
    try:
        # الاتصال بـ Overpass API
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        way(around:50,{lat},{lon})["highway"];
        out tags;
        """
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
        response.raise_for_status() # التأكد من عدم وجود خطأ في الاتصال
        data = response.json()
        
        # التأكد من وجود عناصر في الاستجابة
        if not data.get('elements'):
            raise HTTPException(status_code=404, detail="لا توجد بيانات طريق لهذا الموقع")
            
        tags = data['elements'][0]['tags']
        
        # استخراج البيانات مع قيم افتراضية آمنة
        lanes = int(tags.get('lanes', 2))
        maxspeed_str = tags.get('maxspeed', '60')
        # تنظيف سرعة الطريق (قد تحتوي على وحدات مثل '60 mph')
        maxspeed = int(''.join(filter(str.isdigit, maxspeed_str))) if maxspeed_str else 60
        
        length = 500
        highway_encoded = 1 if tags.get('highway') in ['primary', 'motorway'] else 0
        
        # التنبؤ
        df = pd.DataFrame([[length, lanes, maxspeed, highway_encoded, hour]], 
                          columns=['length', 'lanes', 'maxspeed', 'highway_encoded', 'hour'])
        
        prediction = model.predict(df)
        
        return {
            "status": "success",
            "traffic_level": str(prediction[0]),
            "features": {"lanes": lanes, "maxspeed": maxspeed}
        }
        
    except Exception as e:
        # هذا سيظهر لنا نوع الخطأ بدلاً من Internal Server Error الغامض
        raise HTTPException(status_code=500, detail=str(e))