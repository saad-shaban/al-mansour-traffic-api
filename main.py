from fastapi import FastAPI
import joblib
import pandas as pd

# تحميل النموذج الذي دربناه
model = joblib.load('traffic_model.pkl')
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Traffic AI API is running!"}

@app.get("/predict")
def predict(length: float, lanes: int, maxspeed: int, highway_encoded: int, hour: int):
    # تجهيز البيانات للتنبؤ
    input_data = pd.DataFrame([[length, lanes, maxspeed, highway_encoded, hour]], 
                              columns=['length', 'lanes', 'maxspeed', 'highway_encoded', 'hour'])
    
    # الحصول على التنبؤ
    prediction = model.predict(input_data)[0]
    return {"traffic_level": prediction}