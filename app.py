import random
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_geolocation import streamlit_geolocation
from mock_data import (
    CUPB_LAT, 
    CUPB_LNG, 
    E_RICKSHAWS_DATA, 
    RENTALS_DATA, 
    HOPON_DATA, 
    MARKETPLACE_DATA
)

# ==============================================================================
# APP CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(page_title="Campus Go", page_icon="📍", layout="wide")

# Custom CSS for a clean, modern UI
st.markdown("""
    <style>
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 800; 
        color: #1E3A8A; 
        margin-bottom: 0px; 
    }
    .sub-header { 
        font-size: 1.1rem; 
        color: #475569; 
        margin-bottom: 20px; 
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "user_email" not in st.session_state:
    st.session_state.user_email = "student@cup.edu.in"
if "driver_shift" not in st.session_state:
    st.session_state.driver_shift = False
if "driver_loc" not in st.session_state:
    st.session_state.driver_loc = None
if "simulated_vehicles" not in st.session_state:
    st.session_state.simulated_vehicles = E_RICKSHAWS_DATA
if "rentals" not in st.session_state:
    st.session_state.rentals = RENTALS_DATA
if "hopon" not in st.session_state:
    st.session_state.hopon = HOPON_DATA
if "marketplace" not in st.session_state:
    st.session_state.marketplace = MARKETPLACE_DATA

# ==============================================================================
# HEADER & SIDEBAR NAVIGATION
# ==============================================================================
st.markdown('<p class="main-header">📍 Campus Go</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Unified Campus Mobility & P2P Marketplace • Central University of Punjab</p>', unsafe_allow_html=True)

sidebar = st.sidebar
sidebar.header("Control Panel")
user_email = sidebar.text_input("Current User Email", value=st.session_state.user_email)
st.session_state.user_email = user_email

sidebar.divider()
role_selection = sidebar.radio("Select Interface Mode", ["🎓 Student View", "🛞 Driver Duty Mode"])


# ==============================================================================
# 1. DRIVER DUTY MODE (LIVE HARDWARE INPUT)
# ==============================================================================
if role_selection == "🛞 Driver Duty Mode":
    st.header("Driver Operations Terminal")
    st.info("💡 **Prototype Feature:** Starting your shift captures real hardware GPS coordinates and broadcasts them live to the Student Radar.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Shift Controls")
        if not st.session_state.driver_shift:
            if st.button("🟢 START SHIFT & BROADCAST GPS", use_container_width=True, type="primary"):
                st.session_state.driver_shift = True
                st.rerun()
        else:
            if st.button("🔴 END SHIFT (GO OFFLINE)", use_container_width=True):
                st.session_state.driver_shift = False
                st.session_state.driver_loc = None
                st.rerun()
                
    with col2:
        st.subheader("Telemetry Status")
        if st.session_state.driver_shift:
            st.success("🟢 ACTIVE: Broadcasting Location to Campus Network")
        else:
            st.error("🔴 OFFLINE: Invisible on Student Map")

    st.divider()
    
    if st.session_state.driver_shift:
        st.markdown("### 📡 Live Hardware GPS Capture")
        st.caption("Tap the location button below to ping device coordinates.")
        
        live_loc = streamlit_geolocation()
        
        if live_loc and live_loc.get("latitude"):
            st.session_state.driver_loc = {
                "lat": live_loc["latitude"],
                "lon": live_loc["longitude"]
            }
            st.metric(label="Active GPS Signal", value=f"{live_loc['latitude']:.5f}, {live_loc['longitude']:.5f}")


# ==============================================================================
# 2. STUDENT VIEW (STABLE NATIVE RENDERER)
# ==============================================================================
else:
    # Auto-refreshes data smoothly every 5 seconds (Zero flickering with st.map)
    st_autorefresh(interval=5000, limit=None, key="live_map_sync")

    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Live Transit Radar", "🚲 P2P Rentals", "🛵 Hop-On Sharing", "🏷️ Marketplace"])

    # ------------------ TAB 1: LIVE TRANSIT RADAR ------------------
    with tab1:
        st.subheader("Live Campus Transit Radar")
        st.caption("Native WebGL rendering (Brave Shield compatible, zero screen flickering).")
        
        col_map, col_info = st.columns([2.5, 1])
        
        map_points = []
        
        # Simulate slight live vehicle drift across campus
        for v in st.session_state.simulated_vehicles:
            v["lat"] += random.choice([-0.00004, 0.00004, 0.0])
            v["lng"] += random.choice([-0.00004, 0.00004, 0.0])
            map_points.append({"lat": v["lat"], "lon": v["lng"]})
            
        # Append real driver coordinates if active
        if st.session_state.driver_shift and st.session_state.driver_loc:
            map_points.append({
                "lat": st.session_state.driver_loc["lat"], 
                "lon": st.session_state.driver_loc["lon"]
            })
            
        df_map = pd.DataFrame(map_points)

        with col_map:
            if not df_map.empty:
                # Native Mapbox/Deck.gl map: loads instantly across all browsers
                st.map(df_map, zoom=16, use_container_width=True)
            else:
                st.warning("No active vehicles detected.")
            
        with col_info:
            st.markdown("#### 📡 Active Fleet")
            if st.session_state.driver_shift and st.session_state.driver_loc:
                with st.container(border=True):
                    st.markdown("**🚨 LIVE DEMO DRIVER**")
                    st.caption("Status: Active GPS Stream")
                    st.success("ETA: < 1 min away")
                    
            for v in st.session_state.simulated_vehicles:
                with st.container(border=True):
                    st.markdown(f"**Rickshaw:** `{v['id']}`")
                    st.caption(f"Driver: {v['driver']}")
                    st.info(f"ETA: ~{v['eta_min']} mins")

    # ------------------ TAB 2: P2P RENTALS ------------------
    with tab2:
        st.subheader("Short-Term Vehicle Rentals")
        
        with st.expander("➕ List Your Vehicle for Rent", expanded=False):
            with st.form("rent_form", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                v_title = col_f1.text_input("Vehicle Model", placeholder="e.g. Hero Hawk 21-Speed")
                v_type = col_f2.selectbox("Type", ["Bicycle", "Scooty", "Motorbike"])
                v_rate = col_f1.number_input("Rate (₹)", min_value=5, value=10, step=5)
                v_unit = col_f2.selectbox("Per", ["hr", "day"])
                v_loc = st.text_input("Pickup Location", placeholder="e.g. Hostel 3 Rack")
                
                if st.form_submit_button("📢 Publish Rental", type="primary") and v_title and v_loc:
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
                    st.success("Vehicle published to campus network!")
                    st.rerun()

        st.markdown("#### Available Vehicles")
        available_rentals = [r for r in st.session_state.rentals if r["status"] == "Available"]
        
        col_r1, col_r2 = st.columns(2)
        for idx, r in enumerate(available_rentals):
            with (col_r1 if idx % 2 == 0 else col_r2).container(border=True):
                st.markdown(f"### {r['title']} (`{r['type']}`)")
                st.markdown(f"**Rate:** ₹{r['rate']}/{r['unit']} | **Location:** {r['location']}")
                st.caption(f"Owner: {r['owner']}")
                if st.button("🔑 Reserve Vehicle", key=f"rent_{r['id']}", use_container_width=True):
                    r["status"] = "Rented"
                    st.rerun()

    # ------------------ TAB 3: HOP-ON RIDE SHARE ------------------
    with tab3:
        st.subheader("Campus Hop-On Sharing")
        
        col_hop_ctrl, col_hop_list = st.columns([1, 2])
        
        with col_hop_ctrl:
            women_only_filter = st.checkbox("🛡️ Women-Only Rides")
            st.divider()
            st.markdown("#### Offer a Pillion Seat")
            with st.form("hopon_form", clear_on_submit=True):
                h_from = st.text_input("From", value="Hostel 3")
                h_to = st.text_input("To", value="Academic Block")
                h_time = st.text_input("Departure Time", value="10:00 AM")
                h_women = st.checkbox("Women-Only Ride")
                h_tag = st.selectbox("Tag", ["Helmet Provided", "Silent Commute", "Fast Commute"])
                if st.form_submit_button("🚀 Publish Ride", type="primary"):
                    st.session_state.hopon.append({
                        "id": f"H0{len(st.session_state.hopon)+1}",
                        "driver": st.session_state.user_email.split('@')[0],
                        "from": h_from, "to": h_to, "time": h_time,
                        "women_only": h_women, "seats": 1, "tag": h_tag
                    })
                    st.rerun()

        with col_hop_list:
            filtered_rides = st.session_state.hopon
            if women_only_filter:
                filtered_rides = [h for h in filtered_rides if h["women_only"]]
                
            for h in filtered_rides:
                with st.container(border=True):
                    badge = "🛡️ Women-to-Women" if h['women_only'] else "🌐 Open to All"
                    st.markdown(f"#### {h['from']} ➔ {h['to']}")
                    st.write(f"⏰ **{h['time']}** | {badge} | Tag: `{h['tag']}`")
                    st.caption(f"Rider: {h['driver']}")
                    if st.button(f"🛵 Request Seat ({h['seats']} Free)", key=f"hop_{h['id']}"):
                        st.success("Seat request sent to rider!")

    # ------------------ TAB 4: MARKETPLACE ------------------
    with tab4:
        st.subheader("Student Second-Hand Marketplace")
        
        with st.expander("📦 Sell an Item", expanded=False):
            with st.form("sell_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                m_title = c1.text_input("Item Title", placeholder="e.g. Engineering Drafter")
                m_cat = c2.selectbox("Category", ["Academic Gear", "Vehicles", "Accessories"])
                m_price = c1.number_input("Price (₹)", min_value=0, value=250, step=50)
                m_cond = c2.selectbox("Condition", ["Brand New", "Like New", "Used - Good", "Fair"])
                m_desc = st.text_input("Short Description")
                if st.form_submit_button("Post Listing", type="primary") and m_title:
                    st.session_state.marketplace.append({
                        "id": f"M0{len(st.session_state.marketplace)+1}",
                        "title": m_title, "category": m_cat, "price": m_price,
                        "condition": m_cond, "seller": st.session_state.user_email, "desc": m_desc
                    })
                    st.rerun()

        st.markdown("#### Live Marketplace Listings")
        grid_cols = st.columns(3)
        for idx, item in enumerate(st.session_state.marketplace):
            with grid_cols[idx % 3].container(border=True):
                st.markdown(f"**{item['title']}**")
                st.markdown(f"## ₹{item['price']}")
                st.caption(f"Condition: {item['condition']}")
                st.write(f"_{item['desc']}_")
                mailto_link = f"mailto:{item['seller']}?subject=Campus Go Listing: {item['title']}"
                st.link_button("✉️ Contact Seller", mailto_link, use_container_width=True)
