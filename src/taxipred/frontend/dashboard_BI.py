import streamlit as st
from streamlit_option_menu import option_menu
from taxipred.utils.helpers import read_api_endpoint #post_api_endpoint
from taxipred.utils.helpers import to_is_weekend, to_day_label, divide_time_of_day, is_business_hour
import pandas as pd
from taxipred.backend.data_processing import TaxiPriceBI, FareRequest, TaxiPricePredictor
from datetime import date, datetime
from taxipred.utils.constants import IMG_PATH


data = read_api_endpoint("api/taxi")

def show_home():
    c1, c2, c3 = st.columns([1, 2, 1])
    # html/CSS injections for UX
    with c2:
        st.markdown(
    """
    <div style="text-align:center;">
        <h1 style="margin-bottom:5px;">RESEKOLLEN AB</h1>
        <p style="margin-top:0; font-size:20px;">– din restjänst för alla tillfällen –</p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.image(str(IMG_PATH), use_container_width=True, output_format="auto")


def show_taxikollen():
    st.title("Taxikollen")
    st.markdown("##### Här väljer du dina resdetaljer. ")
    st.markdown("##### Klicka sedan på 'Predict Taxi Price' så estimerar vi ditt respris i realtid.")
    travel_date = st.date_input("Välj resdatum: ", value=date.today())
    default_time = datetime.now().time().replace(second=0, microsecond=0)
    travel_time = st.time_input("Välj klockslag: ", value=default_time)
    travel_passenger = st.number_input("Välj antal resenärer: ", min_value=1, max_value=6, value=1, step=1)

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
            "Passenger_Count": int(travel_passenger)
        }

    #response = post_api_endpoint(payload, endpoint="/api/taxi/predict")
    #predicted_price = response.json().get("predicted_price")

        st.markdown(f"Predicted taxi price:")

def show_bi():
    st.title("BI Taxikollen (begränsad)")
    st.info("KPI:er, grafer och tabeller för BI.")
    #st.dataframe(df)

# --- Side menu for option_menu for selecting Predict or BI ------#
with st.sidebar:
    selected = option_menu(
        menu_title="Välj användare",
        options=["Home", "Taxikollen", "BI Taxikollen (begränsad)"],
        icons=["house", "taxi-front-fill", "graph-up-arrow"],
        menu_icon="chat-left-text",
        default_index=0,
                styles={
            "container": {"padding": "5px", "background-color": "#f0f2f6"},
            "icon": {"color": "#002147", "font-size": "20px"},  # marinblå ikon
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "color": "black"
            },
            "nav-link-selected": {
                "background-color": "#002147",  # marinblå bakgrund för aktivt val
                "color": "white"                # vit text
            },
        }
    )
#st.write(f"Du valde: {selected}")
# ---- Initial front page with company name, image and slogan -------

#st.image(ASSETS_PATH / taxi_bild.jpg)



#df = pd.DataFrame(data.json())

# @st.cache_data
# def load_df(path:str):
#     return pd.read_csv(path)

# df = load_df(DF_PATH)
# bi = TaxiPriceBI(df)


# --- router for main page selector ------
if selected == "BI Taxikollen (begränsad)":
    show_bi()
elif selected == "Taxikollen":
    show_taxikollen()
else:
    show_home()

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














#if __name__ == "__main__":
#   main()
