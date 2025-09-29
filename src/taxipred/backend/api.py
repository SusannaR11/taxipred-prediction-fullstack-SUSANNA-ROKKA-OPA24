from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
from pydantic import BaseModel, Field
import joblib
import numpy as np
#from .data_processing import ()

app = FastAPI()

taxi_data = TaxiData()

@app.get("/taxi/")
async def read_taxi_data():
    return taxi_data.to_json()

@app.get("/taxi/bi/opportunities")
async def opportunities():
    return opportunities.to_json()