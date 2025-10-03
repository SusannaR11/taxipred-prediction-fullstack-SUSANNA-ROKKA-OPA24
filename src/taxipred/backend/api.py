from fastapi import FastAPI
import pandas as pd
from taxipred.backend.data_processing import TaxiData, FareRequest, PredictionOutput, TripDurationCalculator, FareRateTable
from pydantic import BaseModel, Field
import joblib
import numpy as np
from taxipred.utils.constants import MODELS_PATH

app = FastAPI()
taxi_data = TaxiData()
tripdur_calc = TripDurationCalculator(taxi_data.df)
rate_table = FareRateTable(taxi_data.df)

# the feature order model was trained in
FEATURE_ORDER = [
    "Trip_Distance_km","Passenger_Count","Base_Fare",
    "Per_Km_Rate","Per_Minute_Rate","Trip_Duration_Minutes"
] 

@app.get("/api/taxi/")
def read_taxi_data():
    return taxi_data.to_json()

@app.get("/api/taxi/rates")
def rates(passengers: int):
    return rate_table.get(passengers)

@app.post("/api/taxi/predict", response_model=PredictionOutput)
def predicted_price(payload: FareRequest):
    rates = rate_table.get(payload.Passenger_Count) # added
    duration = tripdur_calc.tripduration(payload.Trip_Distance_km) #added
    #data_to_predict = pd.DataFrame([payload.model_dump()]) #removed
    row = {**payload.model_dump(), **rates, "Trip_Duration_Minutes": duration} #added
    X = pd.DataFrame([row], columns=FEATURE_ORDER, dtype=float) #added
    rf = joblib.load(MODELS_PATH / "taxi_rf_model.joblib")
    y = rf.predict(X)
    #prediction = rf.predict(data_to_predict) # removed
    #return{"predicted_price": prediction[0]} # removed
    return {"predicted_price": float(y[0])}
  
  
#@app.get("api/taxi/predict/")
#async def bi_opportunities():
#    return bi_opportunities.to_json()

#@app.post("api/taxi/predict/bi")

