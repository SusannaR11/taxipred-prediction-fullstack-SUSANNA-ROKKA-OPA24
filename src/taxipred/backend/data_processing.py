from taxipred.utils.constants import TAXI_CSV_PATH
from pathlib import Path
import pandas as pd
import json
import joblib
from pydantic import BaseModel, Field
import numpy as np
from typing import Dict, Tuple

CSV_PATH = TAXI_CSV_PATH / "df_BI.csv"

BI_BINARY_COLS = ["IsBusinessHour", "IsRain", "IsSnow", "IsWeekend"]
TARGET_COL = "Trip_Price"


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

# calculates tripduration based on distance_km user input
class TripDurationCalculator:
    def __init__(self, df):
        mins_per_km = (df["Trip_Duration_Minutes"] / df["Trip_Distance_km"]).median()
        self._min_per_km = float(mins_per_km)

    def tripduration(self, distance_km: float) -> float:
        # just in case to not send value 0 to model
        return max(float(distance_km) * self._min_per_km, 1.0)       

# calculates Base_Fare, Per_km_Rate, Per_Minute_Rate using passenger_count # based on user input in UI
class FareRateTable:
    def __init__(self, df: pd.DataFrame):
        rate_cols = ["Base_Fare", "Per_Km_Rate", "Per_Minute_Rate"]
        # calculate median per passenger
        self.by_pax = df.groupby("Passenger_Count")[rate_cols].median()
        self.by_pax.index = self.by_pax.index.astype(float)
        self.overall = df[rate_cols].median().to_dict()
    
#fallback in case input is other than training data (ie 1-6)
    def get(self, passengers: int | float) -> dict:
        p = float(passengers)
        if p in self.by_pax.index:
            return self.by_pax.loc[p].to_dict()
        return self.overall
        

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
# ------ uplifts: rain, snow, weekend, businesshour
class BIUplifts:
    def __init__(self, csv_path: Path = CSV_PATH):
        self.df = pd.read_csv(csv_path)
        self.df.columns = [str(c).strip() for c in self.df.columns]
        self.uplift_percent: Dict[str, float] = {}
        for col in BI_BINARY_COLS:
            m1 = self.df.loc[self.df[col] == 1, TARGET_COL].mean()
            m0 = self.df.loc[self.df[col] == 0, TARGET_COL].mean()
            percent = ((m1-m0) / m0) * 100.0
            self.uplift_percent[col] = float(percent)
    
    def apply(self, base_price: float, flags: Dict[str, int]) -> Tuple[Dict[str, float],float, float]:
        applied = {}
        adjust = float (base_price)
        for col in BI_BINARY_COLS:
            percent = self.uplift_percent.get(col, 0.0)if int(flags.get(col, 0)) == 1 else 0.0
            applied[col] = percent
            if percent !=0.0:
                adjust *= (1.0 + percent / 100.0)
        uplift_total_percent = 0.0 if base_price <= 0 else (adjust / base_price - 1.0) * 100.0
        return applied, round(uplift_total_percent, 2), round(adjust, 2)






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