import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
from taxipred.backend.data_processing import TaxiPriceBI, FareRequest, TaxiPricePredictor


data = read_api_endpoint("taxi")

df = pd.DataFrame(data.json())

DF_PATH = "explorations/df_integrate_unknown.csv"

@st.cache_data
def load_df(path:str):
    return pd.read_csv(path)

df = load_df(DF_PATH)
bi = TaxiPriceBI(df)

# what-if sandbox utlising outlier scenarious for business opportunities
def main():
    st.markdown("# Taxi Prediction BI Dashboard")

    st.dataframe(df)

    feature = st.selectbox(
        "Feature",
        ["Weather", "Day_of_Week", "Traffic_Conditions", "Time_of_Day"]
    )
    values = sorted(df[feature].dropna().unique().tolist())
    value = st.selectbox("Value", values)

    st.divider()
    st.subheader("Single feature uplift")
    feature = st.selectbox("Feature", ["Weather","Day_of_Week","Traffic_Conditions","Time_of_Day"])
    values = sorted(df[feature].dropna().unique().tolist())
    value = st.selectbox("Value", values)
    if st.button("Calculate uplift"):
        res = bi.uplift(feature, value)
        st.metric(f"{feature} = {value}", f"${res['avg_fare']}", f"{res['uplift_pct']}% vs baseline")
        st.json(res)

    if st.button("Calculate uplift opportunity"):
        res = bi.uplift(feature, value)
        st.metric(
            f"{feature} = {value}",
            f"${res['avg_fare']}",
            f"{res['uplift_pct']}% vs baseline"
        )
        st.caption(f"Sample size: {res['count']} rows")
        st.json(res)

    st.divider()
    st.subheader("Uplift calculator")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        weather = st.selectbox("Weather", sorted(d["Weather"].dropna().unique()))
    with c2:
        dow= st.selectbox("Day_of_Week", sorted(df["Day_of_Week"].dropna().unique()))
    with c3:
        traffic = st.selectbox("Traffic_Conditions", sorted(df["Traffic_Conditons"].dropna().unique()))
    with c4:
        tod = st.selectbox("Time_of_Day", sorted(df["Time_of_Day"].dropna().unique()))

    if st.button("Calculate combo uplift"):
        res = bi.uplift_combo({"Weather": weather, "Day_of_Week": dow, "Traffic_Conditions": traffic, "Time_of_Day": tod})
        st.metric("Combo avg fare", f"${res['avg_fare']}", f"{res['uplift_pct']}% vs baseline")
        st.caption(f"Sample size: {res['count']} rows")
        st.json(res)
    


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
