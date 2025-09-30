import streamlit as st
from taxipred.utils.helpers import read_api_endpoint #post_api_endpoint
from taxipred.utils.helpers import to_is_weekend, to_day_label, divide_time_of_day, is_business_hour
import pandas as pd
from taxipred.backend.data_processing import TaxiPriceBI, FareRequest, TaxiPricePredictor
from datetime import date, datetime


data = read_api_endpoint("api/taxi")

#df = pd.DataFrame(data.json())

# @st.cache_data
# def load_df(path:str):
#     return pd.read_csv(path)

# df = load_df(DF_PATH)
# bi = TaxiPriceBI(df)

# 
# what-if sandbox utlising outlier scenarious for business opportunities
def main():
    st.markdown("# Taxi Prediction BI Dashboard")

    #st.dataframe(df)

travel_date = st.date_input("Travel date", value=date.today())
travel_time = st.time_input("What time would you like to travel?", value=datetime.now().time())

if st.button("Predict Taxi Price"):
    day_label = to_day_label(travel_date)
    is_weekend = to_is_weekend(travel_date)
    tod_label, tod_num = divide_time_of_day(travel_time)
    business_hour = is_business_hour(travel_time)

    payload = {
        #     "Trip_Distance_km": Trip_Distance_km,
        #     "Day_of_Week": Day_of_Week,
        #     "Time_of_Day": Time_of_Day,
        #     "Passenger_Count": Passenger_Count
        #
        "IsWeekend": is_weekend,
        "Time_of_Day": tod_label,
        "Time_of_Day_Num": tod_num,
        "IsBusinessHour": business_hour,
    }

    #response = post_api_endpoint(payload, endpoint="/api/taxi/predict")
    #predicted_price = response.json().get("predicted_price")

    st.markdown(f"Predicted taxi price:")

#     feature = st.selectbox(
#         "Feature",
#         ["Weather", "Day_of_Week", "Traffic_Conditions", "Time_of_Day"]
#     )
#     values = sorted(df[feature].dropna().unique().tolist())
#     value = st.selectbox("Value", values)

#     st.divider()
#     st.subheader("Single feature uplift")
#     feature = st.selectbox("Feature", ["Weather","Day_of_Week","Traffic_Conditions","Time_of_Day"])
#     values = sorted(df[feature].dropna().unique().tolist())
#     value = st.selectbox("Value", values)
#     if st.button("Calculate uplift"):
#         res = bi.uplift(feature, value)
#         st.metric(f"{feature} = {value}", f"${res['avg_fare']}", f"{res['uplift_pct']}% vs baseline")
#         st.json(res)

#     if st.button("Calculate uplift opportunity"):
#         res = bi.uplift(feature, value)
#         st.metric(
#             f"{feature} = {value}",
#             f"${res['avg_fare']}",
#             f"{res['uplift_pct']}% vs baseline"
#         )
#         st.caption(f"Sample size: {res['count']} rows")
#         st.json(res)

#     st.divider()
#     st.subheader("Uplift calculator")
#     c1, c2, c3, c4 = st.columns(4)
#     with c1:
#         weather = st.selectbox("Weather", sorted(d["Weather"].dropna().unique()))
#     with c2:
#         dow= st.selectbox("Day_of_Week", sorted(df["Day_of_Week"].dropna().unique()))
#     with c3:
#         traffic = st.selectbox("Traffic_Conditions", sorted(df["Traffic_Conditons"].dropna().unique()))
#     with c4:
#         tod = st.selectbox("Time_of_Day", sorted(df["Time_of_Day"].dropna().unique()))

#     if st.button("Calculate combo uplift"):
#         res = bi.uplift_combo({"Weather": weather, "Day_of_Week": dow, "Traffic_Conditions": traffic, "Time_of_Day": tod})
#         st.metric("Combo avg fare", f"${res['avg_fare']}", f"{res['uplift_pct']}% vs baseline")
#         st.caption(f"Sample size: {res['count']} rows")
#         st.json(res)
    


    # with st.form("Fare_form"):
    #     distance = st.number_input("Trip distance (km)", min_value=0.1, value=10.0)
    #     passengers = st.number_input("Passenger count", min_value=1, max_value=6, value=2)

    #     submitted = st.form_submit_button("Predict Fare")
    
    # if submitted:
    #     req = FareRequest(
    #         Trip_Distance_km=distance,
    #         Passenger_Count=passengers,
    #     )

    # baseline = predictor.predict(req)
    # st.metric("Predicted Fare", f"${baseline:.2f}")

    # #---- uplift calculator ------
    # uplift = bi.uplift_request(req, "IsRain", 1)
    # st.write("What if it rains?")
    # st.json(uplift)














if __name__ == "__main__":
    main()
