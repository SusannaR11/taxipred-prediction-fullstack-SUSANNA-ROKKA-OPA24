from fastapi import FastAPI
import pandas as pd
from taxipred.backend.data_processing import TaxiData, FareRequest, PredictionOutput, TripDurationCalculator
from pydantic import BaseModel, Field
import joblib
import numpy as np
from taxipred.utils.constants import MODELS_PATH

app = FastAPI()
taxi_data = TaxiData()
tripdur_calc = TripDurationCalculator(taxi_data.df)

@app.get("/api/taxi/")
def read_taxi_data():
    return taxi_data.to_json()

@app.post("/api/taxi/predict", response_model=PredictionOutput)
def predicted_price(payload: FareRequest):
    data_to_predict = pd.DataFrame([payload.model_dump()])
    rf = joblib.load(MODELS_PATH / "taxi_rf_model.joblib")
    prediction = rf.predict(data_to_predict)
    return{"predicted_price": prediction[0]}


#@app.get("api/taxi/predict/")
#async def bi_opportunities():
#    return bi_opportunities.to_json()

#@app.post("api/taxi/predict/bi")

