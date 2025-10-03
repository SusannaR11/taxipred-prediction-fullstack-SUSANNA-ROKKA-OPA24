from taxipred.utils.constants import TAXI_CSV_PATH
from pathlib import Path
import pandas as pd
import json
import joblib
from pydantic import BaseModel, Field
import numpy as np

CSV_PATH = TAXI_CSV_PATH / "df_BI.csv"


class TaxiData:
    def __init__(self, csv_path: Path = CSV_PATH):
        try:
            self.df = pd.read_csv(csv_path)
        except FileNotFoundError:
            self.df = pd.DataFrame([
                {"Trip_Distance_km": 5.0, "Trip_Price": 12.5},
                {"Trip_Distance_km": 12.3, "Trip_Price": 28.9},
            ])
    
    def to_json(self):
        return self.df.to_dict(orient = "records")

class TripDurationCalculator:
    def __init__(self, df):
        mins_per_km = (df["Trip_Duration_Minutes"] / df["Trip_Distance_km"]).median()
        self._min_per_km = float(mins_per_km)

    def tripduration(self, distance_km: float) -> float:
        # just in case to not send value 0 to model
        return max(float(distance_km) * self._min_per_km, 1.0)       

 class BaseFare:
    def __init__(self):
        basefare = (df)       

# request/ response schemas THE ONE TO USE
class FareRequest(BaseModel):
    Trip_Distance_km: float = Field(..., ge=0.1)
    Passenger_Count: float = Field(..., ge=1, le=6)
    #Base_Fare: float = Field(..., ge=0.0)
    #Per_Km_Rate: float = Field(..., ge=0.0)
    #Per_Minute_Rate: float = Field(..., ge=0.0)
    #Trip_Duration_Minutes: float = Field(..., ge=1.0)

DEFAULTS = {
    "Base_Fare": 49.0,
    "Per_Km_Rate": 12.0,
    "Per_Minute_Rate": 5.0,
    "Trip_Duration_Minutes": 15.0,
 }

FEATURE_ORDER = [
    "Trip_Distance_km","Passenger_Count","Base_Fare",
    "Per_Km_Rate","Per_Minute_Rate","Trip_Duration_Minutes"
]   

# output
class PredictionOutput(BaseModel):
    predicted_price: float = Field(ge=0)

# class TaxiPricePredictor:
#     def __init__(self, model_path: str):
#         self.model = joblib.load(model_path)
    
#     def predict(self, request: FareRequest) -> float:
#         # convert pydantic model -> dict (json) -> dataframe(????)
#         X = pd.DataFrame([request.dict()])
#         y_pred = self.model.predict(X)[0]
#         return float(y_pred)

# # ----- BI data-processing ------
# # smart features and outlier analysis:
# class TaxiPriceBI:
#     def __init__(self, df: pd.DataFrame):
#         self.df = df 
#         self._baseline = float(df["Trip_Price"].mean())
    
#     def baseline(self) -> float:
#         return self._baseline
    
#     def uplift_request(self, feature: str, value) -> dict:
#         base = self._baseline
#         avg = self.df[self.df[feature] == value]["Tripe_Price"].mean()
#         pct = ((avg - base) / base) *100
#         return{
#             "feature": feature,
#             "value": value,
#             "avg_fare": round(float(avg),2),
#             "baseline": round(base, 2),
#             "uplift_pct": round(float(pct), 2),
#             "count": int((self.df[feature] == value).sum())
#         }


#     def uplift_combo(self, conditions: dict) -> dict:
#         #Average fare for multiple conditions at once.
#         base = self._baseline
#         df_f = self.df.copy()
#         for col, val in conditions.items():
#             df_f = df_f[df_f[col] == val]
#         avg = df_f["Trip_Price"].mean()
#         pct = ((avg - base) / base) * 100
#         return {
#             "conditions": conditions,
#             "avg_fare": round(float(avg), 2),
#             "baseline": round(base, 2),
#             "uplift_pct": round(float(pct), 2),
#             "count": int(len(df_f)),
#         }

#     def top_fare_outliers(self, n=5):
#         return self.df.nlargest(n, "Trip_Price").to_dict(orient="records")



if __name__ == "__main__":
    data = TaxiData()
    print(data.to_json())