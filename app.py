import random
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from streamlit_geolocation import streamlit_geolocation
from mock_data import CUPB_LAT, CUPB_LNG, E_RICKSHAWS_DATA, RENTALS_DATA, HOPON_DATA, MARKETPLACE_DATA

st.set_page_config(page_title="Campus Go", page_icon="🛺", layout="wide")

# --- Initialize Session State ---
if "user_email" not in st.session_state:
    st.session_state.user_email = "student@cup.edu.in"
if "driver_shift" not in st.session_state:
    st.session_state.driver_shift = False
if "rentals" not in st.session_state:
    st.session_state.rentals = RENTALS_DATA
if "hopon" not in st.session_state:
    st.session_state.hopon = HOPON_DATA
if "marketplace" not in st.session_state:
    st.session_state.marketplace = MARKETPLACE_DATA

# --- Header & Sidebar ---
st.title("🛺 Campus Go")
st.caption("Unified Campus Mobility Platform • Central University of Punjab")

sidebar = st.sidebar
sidebar.header("User Access")
user_email = sidebar.text_input("Institutional Email", value=st.session_state.user_email)
st.session_state.user_email = user_email
role_selection = sidebar.radio("App View", ["Student View", "Driver Duty Mode"])

# ==================== DRIVER DUTY MODE ====================
if role_selection == "Driver Duty Mode":
    st.subheader("🛺 E-Rickshaw Driver Terminal")
    st.info("Zero-Distraction Mode Active. Keep device mounted on dashboard.")
    
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.driver_shift:
            if st.button("🟢 START SHIFT", use_container_width=True):
                st.session_state.driver_shift = True
                st.rerun()
        else:
            if st.button("🔴 END SHIFT", use_container_width=True):
                st.session_state.driver_shift = False
                st.rerun()
                
    with col2:
        status_str = "🟢 Active & Broadcasting GPS" if st.session_state.driver_shift else "🔴 Offline"
        st.metric(label="Duty Status", value=status_str)

    st.divider()
    st.markdown("### 📡 Hardware GPS Telemetry")
    location = streamlit_geolocation()
    if location and location.get("latitude"):
        st.success(f"GPS Signal Active: Lat {location['latitude']:.5f}, Long {location['longitude']:.5f}")
    else:
        st.caption("Tap location icon above to allow tablet GPS streaming.")

# ==================== STUDENT VIEW ====================
else:
    # Auto-refresh app every 3 seconds for live tracking
    refresh_count = st_autorefresh(interval=3000, limit=None, key="live_map_sync")

    tab1, tab2, tab3, tab4 = st.tabs(["🛺 Live Transit", "🚲 Rentals", "🛵 Hop-On", "🏷️ Marketplace"])

    # ------------------ TAB 1: LIVE TRANSIT ------------------
    with tab1:
        st.subheader("Live E-Rickshaw Radar")
        col_map, col_info = st.columns([3, 1])
        
        # Simulate slight live movement on each 3-second refresh
        for e in E_RICKSHAWS_DATA:
            e["lat"] += random.choice([-0.00006, 0.00006, 0.0])
            e["lng"] += random.choice([-0.00006, 0.00006, 0.0])

        with col_map:
            # Satellite imagery tiles for detailed campus view
            m = folium.Map(
                location=[CUPB_LAT, CUPB_LNG], 
                zoom_start=17,
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri'
            )
            
            # Central Campus Landmark Marker
            folium.Marker(
                [CUPB_LAT, CUPB_LNG], 
                popup="CUPB Main Academic Block", 
                icon=folium.Icon(color="blue", icon="university", prefix="fa")
            ).add_to(m)
            
            # Active Moving E-Rickshaws
            for e in E_RICKSHAWS_DATA:
                folium.Marker(
                    [e["lat"], e["lng"]],
                    popup=f"E-Rickshaw: {e['id']}\nDriver: {e['driver']}",
                    icon=folium.Icon(color="green", icon="car", prefix="fa")
                ).add_to(m)
                
            st_folium(m, width=800, height=450, key=f"map_{refresh_count}")
            
        with col_info:
            st.markdown("### Nearby Vehicles")
            for e in E_RICKSHAWS_DATA:
                with st.container(border=True):
                    st.markdown(f"**Vehicle:** `{e['id']}`")
                    st.caption(f"Driver: {e['driver']}")
                    st.success(f"ETA: ~{e['eta_min']} mins away")

    # ------------------ TAB 2: RENTALS ------------------
    with tab2:
        st.subheader("P2P Short-Term Vehicle Rentals")
        
        col_list, col_add = st.columns([2, 1])
        
        with col_list:
            available_rentals = [r for r in st.session_state.rentals if r["status"] == "Available"]
            for r in available_rentals:
                with st.container(border=True):
                    st.markdown(f"### {r['title']} (`{r['type']}`)")
                    st.write(f"💰 **Rate:** ₹{r['rate']}/{r['unit']} | 📍 **Location:** {r['location']}")
                    st.caption(f"Owner: {r['owner']}")
                    if st.button(f"🔑 Reserve {r['title']}", key=f"rent_{r['id']}"):
                        r["status"] = "Rented"
                        st.success(f"Reserved! Connect with {r['owner']} at {r['location']} for key handover.")
                        st.rerun()
                        
        with col_add:
            st.markdown("### List Your Vehicle")
            with st.form("rent_form"):
                v_title = st.text_input("Vehicle Model", placeholder="e.g. Hero Hawk 21-Speed")
                v_type = st.selectbox("Type", ["Bicycle", "Scooty", "Motorbike"])
                v_rate = st.number_input("Rate (₹)", min_value=5, value=10, step=5)
                v_unit = st.selectbox("Per", ["hr", "day"])
                v_loc = st.text_input("Pickup Location", placeholder="e.g. Hostel 3 Rack")
                submitted = st.form_submit_button("📢 Publish Rental")
                if submitted and v_title and v_loc:
                    st.session_state.rentals.append({
                        "id": f"R0{len(st.session_state.rentals)+1}",
                        "owner": st.session_state.user_email,
                        "type": v_type,
                        "title": v_title,
                        "rate": v_rate,
                        "unit": v_unit,
                        "location": v_loc,
                        "status": "Available"
                    })
                    st.success("Vehicle listed!")
                    st.rerun()

    # ------------------ TAB 3: HOP-ON ------------------
    with tab3:
        st.subheader("Campus Hop-On (Micro-Pillion Sharing)")
        women_only_filter = st.checkbox("🛡️ Show Women-Only Rides Only")
        
        col_rides, col_offer = st.columns([2, 1])
        
        with col_rides:
            filtered_rides = st.session_state.hopon
            if women_only_filter:
                filtered_rides = [h for h in filtered_rides if h["women_only"]]
                
            for h in filtered_rides:
                with st.container(border=True):
                    badge = "🛡️ Women-to-Women" if h['women_only'] else "🌐 Open to All"
                    st.markdown(f"### {h['from']} ➔ {h['to']}")
                    st.write(f"⏰ **Departure:** {h['time']} | **Filter:** {badge}")
                    st.caption(f"Rider: {h['driver']} | Tag: `{h['tag']}`")
                    if st.button(f"🛵 Request Seat ({h['seats']} Free)", key=f"hop_{h['id']}"):
                        st.success("Seat requested! Rider notified.")

        with col_offer:
            st.markdown("### Offer a Pillion Seat")
            with st.form("hopon_form"):
                h_from = st.text_input("From", value="Hostel 3")
                h_to = st.text_input("To", value="Academic Block")
                h_time = st.text_input("Departure Time", value="10:00 AM")
                h_women = st.checkbox("Women-Only Ride")
                h_tag = st.selectbox("Preference", ["Helmet Provided", "Silent Commute", "Fast Commute"])
                h_sub = st.form_submit_button("🚀 Publish Ride")
                if h_sub:
                    st.session_state.hopon.append({
                        "id": f"H0{len(st.session_state.hopon)+1}",
                        "driver": st.session_state.user_email.split('@')[0],
                        "from": h_from,
                        "to": h_to,
                        "time": h_time,
                        "women_only": h_women,
                        "seats": 1,
                        "tag": h_tag
                    })
                    st.success("Ride published!")
                    st.rerun()

    # ------------------ TAB 4: MARKETPLACE ------------------
    with tab4:
        st.subheader("Second-Hand Marketplace")
        col_cat, col_price = st.columns(2)
        with col_cat:
            selected_cat = st.selectbox("Category Filter", ["All", "Vehicles", "Accessories", "Academic Gear"])
        with col_price:
            max_price = st.slider("Max Price (₹)", min_value=100, max_value=5000, value=5000, step=100)

        col_items, col_sell = st.columns([2, 1])
        
        with col_items:
            m_filtered = st.session_state.marketplace
            if selected_cat != "All":
                m_filtered = [m for m in m_filtered if m["category"] == selected_cat]
            m_filtered = [m for m in m_filtered if m["price"] <= max_price]

            grid_cols = st.columns(2)
            for idx, item in enumerate(m_filtered):
                with grid_cols[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {item['title']}")
                        st.markdown(f"🏷️ **Price:** ₹{item['price']}")
                        st.caption(f"Category: {item['category']} | Condition: {item['condition']}")
                        st.write(f"_{item['desc']}_")
                        st.caption(f"Seller: `{item['seller']}`")
                        mailto_link = f"mailto:{item['seller']}?subject=Inquiry about {item['title']} on Campus Go"
                        st.markdown(f'<a href="{mailto_link}" target="_blank"><button style="width:100%; padding:8px; background-color:#2e7d32; color:white; border:none; border-radius:4px; cursor:pointer;">✉️ Email Seller</button></a>', unsafe_allow_html=True)

        with col_sell:
            st.markdown("### Resell an Item")
            with st.form("sell_form"):
                m_title = st.text_input("Item Title", placeholder="e.g. Helmet / Bicycle")
                m_cat = st.selectbox("Category", ["Vehicles", "Accessories", "Academic Gear"])
                m_price = st.number_input("Selling Price (₹)", min_value=50, value=500, step=50)
                m_cond = st.selectbox("Condition", ["Brand New", "Like New", "Used - Good", "Fair"])
                m_desc = st.text_area("Description", placeholder="Details about condition, age, etc.")
                submit_sell = st.form_submit_button("📦 Post Item")
                if submit_sell and m_title and m_desc:
                    st.session_state.marketplace.append({
                        "id": f"M0{len(st.session_state.marketplace)+1}",
                        "title": m_title,
                        "category": m_cat,
                        "price": m_price,
                        "condition": m_cond,
                        "seller": st.session_state.user_email,
                        "desc": m_desc
                    })
                    st.success("Item posted!")
                    st.rerun()
