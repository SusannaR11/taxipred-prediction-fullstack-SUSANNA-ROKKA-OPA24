import streamlit as st
from streamlit_option_menu import option_menu
from taxipred.utils.helpers import read_api_endpoint, post_api_endpoint
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
    st.title("Taxikollen \U0001F696")
    st.markdown("### Klicka och estimera taxipris i realtid.")
    st.markdown("##### Här väljer du dina resdetaljer: ")


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
    st.title("BI Taxikollen")
    clicked = st.button("Ange kod")
    if clicked:
        st.session_state["bi_unlocked"] = True

#---- Passcode for BI content ----
    # if st.session_state.get("show bi_code"):
    #     code = st.text_input("Skriv kod", type="password")
    #     if st.button("Bekräfta"):
    #         if code == "1234":
    #             st.session_state["bi_unlocked"] = True
    #         else:
    #             st.error("Fel kod")
        
    if st.session_state.get("bi_unlocked"):
        st.info("KPI:er, grafer och tabeller för BI.")
    else:
        st.warning("Den här sidan är låst. Klicka 'Ange kod'. ")
    #st.dataframe(df)

#----- BI uplift toggles --------
    stats = read_api_endpoint("/api/taxi/bi").json()
    st.markdown("## Rörelse i % på taxipris:")
    #st.markdown(f"#### Genomsnittligt taxipris: {stats#['general_mean_price']:.2f} SEK (enligt data)")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a: st.metric("Regn", f"{stats['uplift_percent']['IsRain']:.2f}%")
    with col_b: st.metric("Snö", f"{stats['uplift_percent']['IsSnow']:.2f}%")
    with col_c: st.metric("Kontorstid", f"{stats['uplift_percent']['IsBusinessHour']:.2f}%")
    with col_d: st.metric("Helg", f"{stats['uplift_percent']['IsWeekend']:.2f}%")

    st.divider()   

    base = st.number_input("Skriv ett taxipris (SEK)", min_value=0.0, value=140.0, step=1.0)

    c1, c2, c3, c4 = st.columns(4)
    with c1: rain = st.toggle("Regn", value=False)
    with c2: snow = st.toggle("Snö", value=False)
    with c3: businesshour   = st.toggle("Kontorstid", value=False)
    with c4: weekend = st.toggle("Helg", value=False)
    
    if st.button("Beräkna uplift"):
        payload = {
            "base_price": float(base),
            "IsRain": 1 if rain else 0,
            "IsSnow": 1 if snow else 0,
            "IsWeekend": 1 if weekend else 0,
            "IsBusinessHour": 1 if businesshour else 0,
        }
        res = post_api_endpoint(payload, endpoint="/api/taxi/bi").json()
        st.info(f"Uplift totalt: {res['uplift_total_percent']:.1f}%")
        st.success(f"Nytt pris: {res['adjusted_price']:.2f} SEK")

        a = res["applied"]
        st.caption(
            f"Regn: {a['IsRain']:.2f}%  |  Snö: {a['IsSnow']:.2f}%  |  "
            f"Kontorstid: {a['IsBusinessHour']:.2f}%  |  Helg: {a['IsWeekend']:.2f}%"
        )

# #------- view break down of uplifts ---------
#         applied = res.get("applied", {})
#         st.caption("Uplift per faktor: ")
#         st.write(
#             f"Regn: {applied.get('IsRain', 0):.1f}% | "
#             f"Snö: {applied.get('IsSnow', 0):.1f}% | "
#             f"Helg: {applied.get('IsWeekend', 0):.1f}% | "
#             f"Kontorstid: {applied.get('IsBusinessHour', 0):.1f}% | "
#         )

# --- Side menu for option_menu for selecting Predict or BI ------#
with st.sidebar:
    selected = option_menu(
        menu_title="Välj användare",
        options=["Home", "Taxikollen", "BI Taxikollen (begränsad)"],
        icons=["house", "taxi-front-fill", "graph-up-arrow"],
        menu_icon="chat-left-text",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f2f6"},
            "icon": {"color": "inherit", "font-size": "20px"},  # marinblå ikon
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "color": "black",
                "--hover-color": "#e6e9ef"
            },
            "nav-link-selected": {
                "background-color": "#002147",  # marinblå bakgrund för aktivt val
                "color": "white"                # vit text
            },
        }
    )



# --- router for main page selector ------
if selected == "BI Taxikollen (begränsad)":
    show_bi()
elif selected == "Taxikollen":
    show_taxikollen()
else:
    show_home()










#if __name__ == "__main__":
#   main()
