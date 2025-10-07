from fastapi import FastAPI
import pandas as pd
from taxipred.backend.data_processing import TaxiData, FareRequest, BIUplifts, PredictionOutput, TripDurationCalculator, FareRateTable
from pydantic import BaseModel, Field
import joblib
import numpy as np
from taxipred.utils.constants import MODELS_PATH
from datetime import datetime, timedelta
import requests

app = FastAPI()
taxi_data = TaxiData()
tripdur_calc = TripDurationCalculator(taxi_data.df)
rate_table = FareRateTable(taxi_data.df)
bi_uplifts = BIUplifts()

# cache rate and timestamp (for 1 hour)
# cache so that the web request does not keep hitting the API over and over
_fx_cache = {"rate": None, "ts": None}

def get_usd_to_sek() -> float:
    now = datetime.utcnow()
    if _fx_cache["rate"] and _fx_cache["ts"] and now - _fx_cache["ts"] < timedelta(hours=1):
        return _fx_cache["rate"]
    r = requests.get("https://api.frankfurter.dev/v1/latest",
        params={"base": "USD", "symbols": "SEK"},
        timeout=5)
    r.raise_for_status()
    rate = float(r.json()["rates"]["SEK"])
    _fx_cache.update({"rate": rate, "ts": now})
    return rate


# the feature order model was trained in
FEATURE_ORDER = [
    "Trip_Distance_km","Passenger_Count","Base_Fare",
    "Per_Km_Rate","Per_Minute_Rate","Trip_Duration_Minutes"
] 

class BIApplyRequest(BaseModel):
    base_price: float
    IsBusinesssHour: int=0
    IsRain: int= 0
    IsSnow: int= 0
    IsWeekend: int = 0
    

class BIApplyResponse(BaseModel):
    base_price: float
    uplift_total_percent: float
    adjusted_price: float
    applied: dict


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
    # convert usd to sek:
    y_usd = float(y[0])
    usd_sek = get_usd_to_sek()
    y_sek = y_usd * usd_sek
    #prediction = rf.predict(data_to_predict) # removed
    #return{"predicted_price": prediction[0]} # removed
    return {"predicted_price": y_sek}
  
@app.post("/api/taxi/bi", response_model=BIApplyResponse)
def bi_apply(req: BIApplyRequest):
    flags = {
        "IsBusinesssHour": req.IsBusinesssHour,
        "IsRain": req.IsRain,
        "IsSnow": req.IsSnow,
        "IsWeekend": req.IsWeekend,

    }
    applied, total_percent, adjusted = bi_uplifts.apply(base_price=req.base_price, flags=flags)
    return BIApplyResponse(
        base_price=req.base_price,
        uplift_total_percent=total_percent,
        adjusted_price=adjusted,
        applied=applied,
    )
        




#@app.get("api/taxi/predict/")
#async def bi_opportunities():
#    return bi_opportunities.to_json()

#@app.post("api/taxi/predict/bi")

