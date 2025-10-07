import streamlit as st, requests
from streamlit_option_menu import option_menu
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
from taxipred.utils.helpers import to_is_weekend, to_day_label, divide_time_of_day, is_business_hour
from taxipred.backend.data_processing import FareRequest #TaxiData
from datetime import date, datetime
from taxipred.utils.constants import IMG_PATH
from streamlit_geolocation import streamlit_geolocation
from streamlit_folium import st_folium, folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

@st.cache_resource
def get_geolocator():
    return Nominatim(user_agent="taxikollen")

data = read_api_endpoint("/api/taxi/")

# -------render Gbg map with roads----------------
def render_gbg_map(start_latlon: tuple | None, dest_latlon: tuple | None, start_label: str, dest_label:str):
    m = folium.Map(location=[57.7089, 11.9746], zoom_start=12, tiles="OpenStreetMap")

    points = []
    if start_latlon:
        folium.Marker(start_latlon, popup=f"Från: {start_label}").add_to(m)
        points.append(start_latlon)
    if dest_latlon:
        folium.Marker(dest_latlon, popup=f"Till: {dest_label}").add_to(m)
        points.append(dest_latlon)
  
    # Fit map to markers (if both exist)
    if len(points) >= 2:
        m.fit_bounds(points)

    st_folium(m, width=750, height=520)


def show_home():
    c1, c2, c3 = st.columns([1, 2, 1])
    # html/CSS injections for UX
    with c2:
        st.markdown(
    """
    <div style="text-align:center;">
        <h1 style="margin-bottom:5px;">RESEKOLLEN AB</h1>
        <p style="margin-top:0; font-size:20px;">– din resetjänst för alla tillfällen –</p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.image(str(IMG_PATH), width="stretch", output_format="auto")


def show_taxikollen():
    st.title("Taxikollen")
    st.markdown("#### Här väljer du dina resdetaljer. ")
    st.markdown("##### Klicka på 'Predict Taxi Price' så estimerar vi ditt respris i realtid.")

# ----- GPS + Destination (optional) ----------------
    st.markdown("Startpunkt")
    start_addr = st.text_input(
        "Reser från (adress / postnr /ort):",
        value= st.session_state.get("start_addr", ""),
        key="start_addr_input",
    )
    if st.session_state.get("_prev_start_addr") != start_addr:
        st.session_state["_prev_start_addr"] = start_addr
        st.session_state.pop("start_latlon", None)

    if st.button("Använd min plats"):
        loc = streamlit_geolocation()
        if loc and "lat" in loc and "lon" in loc:
            lat, lon = loc["lat"], loc["lon"]
            try:
                addr= get_geolocator().reverse((lat, lon), language="sv").address
            except Exception:
                addr = f"{lat:.5f}, {lon:.5f}"
            st.session_state.start_latlon = (lat, lon)
            st.session_state.start_addr = addr
            st.success(f"Hittade positionen: {addr}")

    start_latlon = st.session_state.get("start_latlon")
    if not start_latlon and start_addr.strip():
        place = get_geolocator().geocode(f"{start_addr}, Göteborg", language="sv", timeout=10)
        if place:
            start_latlon = (place.latitude, place.longitude)
            st.session_state.start_latlon = start_latlon
        else:
            st.error("Hittade inte adressen.")

    dest_addr = st.text_input("Destination (adress / postnr / ort):")

    # ------ Form with user input (date/time is used in BI module) -----
    with st.form("data"):
        travel_date = st.date_input("Välj resdatum: ", value=date.today())
        default_time = datetime.now().time().replace(second=0, microsecond=0)
        travel_time = st.time_input("Välj klockslag: ", value=default_time)
        travel_passenger = st.number_input("Välj antal resenärer: ", min_value=1, max_value=6, value=1, step=1)

        submitted = st.form_submit_button("Predict Taxi Price")


#--------- Submit: geocode destination, calculate distance, call API -----
    # dest_latlon = None
    # if submitted:
    #     if not start_latlon:
    #         st.error("Saknar startpunkt. Klicka 'Använd min plats' först.")
    #         st.stop()
    #     if not dest_addr.strip():
    #         st.error("Ange destination.")
    #         st.stop()
    if submitted:   
        dest_place= get_geolocator().geocode(f"{dest_addr}, Göteborg", language="sv", timeout=10)
    #     if not dest_place:
    #         st.error("Hittade inte destinationen. Prova 'Gata 1, Stad'.")
    #         st.stop()
        dest_latlon = (dest_place.latitude, dest_place.longitude) 
        
# -----------Straight-distance NOT road distance:      
        km = geodesic(start_latlon, dest_latlon).km

#-------- Payload to API ---------------
        payload = {
            "Trip_Distance_km": float(km),
            "Passenger_Count": float(travel_passenger),
            #"Base_Fare": float = Field(..., ge=0.0),
            #"Per_Km_Rate": float = Field(..., ge=0.0),
            #"Per_Minute_Rate": float = Field(..., ge=0.0),
            #"Trip_Duration_Minutes": float = Field(..., ge=1.0),
            }
        response = post_api_endpoint(payload, endpoint="/api/taxi/predict")
        predicted_price = response.json().get("predicted_price")

        st.session_state.km = float(km)
        st.session_state.predicted_price = float(predicted_price) if predicted_price is not None else None
        st.session_state.dest_latlon = dest_latlon

    if st.session_state.get("km") is not None:
        st.info(f"Avstånd (fågelvägen): {st.session_state['km']:.2f} km")
    if st.session_state.get("predicted_price") is not None:
        st.success(f"Predicted price: {st.session_state['predicted_price']:.2f} SEK")
    
        #------- Live map ------------
    st.markdown("### Göteborg") 
    render_gbg_map(
        start_latlon=start_latlon, 
        dest_latlon=st.session_state.get("dest_latlon", None),        start_label=start_addr or st.session_state.get("start_addr", "Start"),
        dest_label=dest_addr or "Destination")


        # Map
        # map_data = [
        #     {"lat": start_latlon[0], "lon": start_latlon[1]},
        #     {"lat": dest_latlon[0], "lon": dest_latlon[1]}
        # ]
        # st.map(data=map_data)


        # BI-only features -----------
        # day_label = to_day_label(travel_date)
        # is_weekend = to_is_weekend(travel_date)
        # tod_label, tod_num = divide_time_of_day(travel_time)
        # business_hour = is_business_hour(travel_time)
    

    #response = post_api_endpoint(payload, endpoint="/api/taxi/predict")
    #predicted_price = response.json().get("predicted_price")

def show_bi():
    st.title("BI Taxikollen (begränsad)")
    clicked = st.button("Ange kod")
    if clicked:
        st.session_state["bi_unlocked"] = True
        
    if st.session_state.get("bi_unlocked"):
        st.info("KPI:er, grafer och tabeller för BI.")
    else:
        st.warning("Den här sidan är låst. Klicka 'Ange kod'. ")
    #st.dataframe(df)

# --- Side menu for option_menu for selecting Predict or BI ------#
with st.sidebar:
    selected = option_menu(
        menu_title="Välj användare",
        options=["Home", "Taxikollen", "BI Taxikollen (begränsad)"],
        icons=["house", "taxi-front-fill", "graph-up-arrow"],
        menu_icon="chat-left-text",
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

# def get_ip_location():
#     try:
#         ip_data = requests.get("https://ipapi.co/json/").json()
#         return float(ip_data["latitude"]), float(data["longtitude"])
#     except Exception:
#         return None


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
