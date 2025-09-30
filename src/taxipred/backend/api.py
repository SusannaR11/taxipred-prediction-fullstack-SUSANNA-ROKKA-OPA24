from fastapi import FastAPI
import pandas as pd
from taxipred.backend.data_processing import TaxiData # FareRequest, PredictionOutput
from pydantic import BaseModel, Field
import joblib
import numpy as np

app = FastAPI()

taxi_data = TaxiData()

@app.get("/api/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()

#@app.get("api/taxi/bi/")
#async def bi_opportunities():
#    return bi_opportunities.to_json()


