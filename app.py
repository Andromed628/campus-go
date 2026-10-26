import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. PAGE CONFIG & CUSTOM STYLING
# --------------------------------------------------
st.set_page_config(
    page_title="CampusWheel | Campus Mobility",
    page_icon="🧭",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    .title-text {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle-text { color: #8b949e; font-size: 0.95rem; margin-bottom: 20px; }
    .custom-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 10px; padding: 15px; margin-bottom: 12px;
    }
    .badge {
        background: rgba(56, 189, 248, 0.15); color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;
    }
    .badge-driver {
        background: rgba(234, 179, 8, 0.15); color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.4);
        padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;
    }
    .card-open {
        background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    .card-full {
        background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. SHARED GLOBAL BACKEND MEMORY (MULTIPLE DEVICES SYNC HERE)
# --------------------------------------------------
@st.cache_resource
def get_global_database():
    return {
        "shuttles": [
            {
                "Vehicle": "⚡ E-Cart #1 (Hostel Shuttle)",
                "lat": 30.1553, "lon": 74.9387,
                "Status": "Moving -> Academic Block",
                "Speed": "14 km/h",
                "Vacant_Seats": "🟢 3 Seats Available",
                "Driver_Email": "driver.harpreet@cup.edu.in",
                "Last_Sync": "12:28 PM"
            },
            {
                "Vehicle": "⚡ E-Cart #2 (Library Line)",
                "lat": 30.1538, "lon": 74.9365,
                "Status": "Boarding at Hostel 3",
                "Speed": "0 km/h",
                "Vacant_Seats": "🔴 Vehicle Full",
                "Driver_Email": "driver.gurpreet@cup.edu.in",
                "Last_Sync": "12:25 PM"
            },
            {
                "Vehicle": "🚌 Main Gate Express",
                "lat": 30.1570, "lon": 74.9405,
                "Status": "Arriving Main Gate",
                "Speed": "18 km/h",
                "Vacant_Seats": "🟢 2 Seats Available",
                "Driver_Email": "driver.singh@cup.edu.in",
                "Last_Sync": "12:20 PM"
            }
        ],
        "demand_pings": {
            "Central Canteen": 14,
            "RLB Girls Hostel": 8,
            "Academic Block / Library": 5,
            "Main Gate": 2
        },
        "vehicles": [
            {"id": "RNT-101", "model": "Hero Hawk 21-Speed", "type": "Bicycle", "rate": 10, "location": "Hostel 3 Rack", "security": "Student ID", "owner": "sneha@cup.edu.in", "status": "Available"},
            {"id": "RNT-102", "model": "TVS Jupiter 125", "type": "Scooty", "rate": 35, "location": "Main Gate", "security": "₹500 Deposit", "owner": "rahul@cup.edu.in", "status": "Available"}
        ],
        "active_rentals": [],
        "rides": [
            {"id": "RIDE-1", "driver": "rahul@cup.edu.in", "from_loc": "Hostel 3", "to_loc": "Academic Block", "time": "09:15 AM", "seats": 2, "vehicle": "TVS Jupiter", "contact": "9876543210"},
            {"id": "RIDE-2", "driver": "priya@cup.edu.in", "from_loc": "Main Gate", "to_loc": "Library", "time": "10:30 AM", "seats": 1, "vehicle": "Electric Scooter", "contact": "9123456789"}
        ],
        "market_items": [
            {
                "id": "MKT-1", "title": "Hercules Roadeo MTB", "category": "Bicycles", 
                "price": 2400, "seller": "sneha@cup.edu.in", "condition": "Good", 
                "location": "Hostel 2", "image": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500"
            }
        ]
    }

db = get_global_database()

# --------------------------------------------------
# 3. MODALS
# --------------------------------------------------
@st.dialog("⚡ Confirm Vehicle Reservation")
def reservation_modal(v):
    st.write(f"### {v['model']} ({v['type']})")
    st.write(f"💵 Rate: ₹{v['rate']}/hr | 📍 Location: {v['location']}")
    st.write(f"🔒 Security Hold Required: `{v['security']}`")
    phone = st.text_input("Mobile Number")
    duration = st.text_input("Duration (Hours)", value="2")
    if st.button("🚀 Confirm Booking", type="primary", use_container_width=True):
        if phone:
            v["status"] = "Reserved"
            db["active_rentals"].append({
                "booking_id": f"BK-{v['id']}",
                "vehicle": v, "phone": phone, "duration": duration,
                "payment_status": "Pending", "before_photo": None, "after_photo": None,
                "pre_notes": "", "post_notes": ""
            })
            st.success("Reserved successfully!")
            st.rerun()
        else:
            st.error("Please enter phone number.")

@st.dialog("🚗 Hop-On Ride Booking")
def hopon_modal(r):
    st.write(f"### {r['from_loc']} ➔ {r['to_loc']}")
    st.write(f"⏰ Departure: {r['time']} | 🚘 {r['vehicle']}")
    st.write(f"👤 Driver: {r['driver']} | 📞 Contact: {r['contact']}")
    phone = st.text_input("Your Contact Number")
    if st.button("🤝 Confirm Hop-On Request", type="primary", use_container_width=True):
        if phone:
            r["seats"] -= 1
            st.success(f"Confirmed! Call driver at {r['contact']}")
            st.rerun()
        else:
            st.error("Please enter contact number.")

# --------------------------------------------------
# 4. SIDEBAR - USER IDENTITY & MODE SWITCHER
# --------------------------------------------------
with st.sidebar:
    st.title("🧭 CampusWheel Control")
    user_email = st.text_input("Log In As (Email)", value="sneha@cup.edu.in")
    st.caption(f"Connected Identity: `{user_email}`")
    st.divider()
    interface_mode = st.radio(
        "Select Active Interface Mode",
        ["🧑‍🎓 Student Mode", "🛺 Driver Duty Mode"],
        index=0
    )
    st.divider()
    if st.button("🔄 Pull Latest Cloud Sync", use_container_width=True):
        st.rerun()

st.markdown('<div class="title-text">CampusWheel</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Campus Mobility & Vehicle Marketplace • Central University of Punjab</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 5. DRIVER DUTY MODE DASHBOARD
# --------------------------------------------------
if interface_mode == "🛺 Driver Duty Mode":
    st.markdown('<span class="badge-driver">🛺 DRIVER DUTY CONTROL PANEL</span>', unsafe_allow_html=True)
    st.write("")
    st.info(f"👨‍✈️ **Active Driver Session:** `{user_email}`")
    
    st.subheader("🚌 Manage Campus Shuttle GPS & Seat Vacancy Telemetry")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        shuttle_names = [s["Vehicle"] for s in db["shuttles"]]
        selected_shuttle = st.selectbox("Select Assigned Vehicle", shuttle_names)
        new_status = st.selectbox("Current Route Status", [
            "Moving -> Academic Block",
            "Boarding at Hostel 3",
            "Boarding at Main Gate",
            "Moving -> Central Library",
            "Idle at Parking"
        ])
        v_seat_status = st.radio("Broadcast Vacant Seat Status to Map", ["🟢 Seats Open", "🔴 Vehicle Full"], horizontal=True)

    with col_d2:
        new_speed = st.slider("Current Speed (km/h)", 0, 30, 14)
        if v_seat_status == "🟢 Seats Open":
            v_count = st.slider("Available Seats Count", 1, 4, 3)
            formatted_seat_str = f"🟢 {v_count} Seats Available"
        else:
            formatted_seat_str = "🔴 Vehicle Full"
            st.caption("Broadcasting: **🔴 Vehicle Full** to Student Radar")
            
        lat_shift = st.slider("Simulate Live GPS Movement (Latitude Offset)", -0.0050, 0.0050, 0.0000, step=0.0005)
    
    if st.button("📡 Broadcast Live GPS & Vacancy to Campus Cloud", type="primary"):
        for s in db["shuttles"]:
            if s["Vehicle"] == selected_shuttle:
                s["Status"] = new_status
                s["Speed"] = f"{new_speed} km/h"
                s["Vacant_Seats"] = formatted_seat_str
                s["lat"] = round(30.1553 + lat_shift, 4)
                s["Driver_Email"] = user_email
                s["Last_Sync"] = "Just Now"
        st.success(f"Broadcasted live telemetry for {selected_shuttle}! Seat Status: {formatted_seat_str}")
        st.rerun()

    st.divider()
    st.subheader("🔥 Live Student Demand Heatmap (Student Crowd Pings)")
    st.caption("Real-time passenger clusters aggregated from student 'I'm Waiting' votes:")
    
    h_cols = st.columns(4)
    for idx, (location, count) in enumerate(db["demand_pings"].items()):
        with h_cols[idx % 4]:
            st.metric(label=f"📍 {location}", value=f"{count} Waiting")

    st.divider()
    st.subheader("📋 Active Passenger Hop-On Requests")
    st.dataframe(pd.DataFrame(db["rides"]), use_container_width=True, hide_index=True)

# --------------------------------------------------
# 6. STUDENT MODE DASHBOARD (4 TABS)
# --------------------------------------------------
else:
    t1, t2, t3, t4 = st.tabs(["🛰️ Live Radar", "🛵 P2P Rentals", "🚗 Hop-On Sharing", "🚲 Marketplace"])

    # TAB 1: LIVE RADAR
    with t1:
        st.subheader("🛰️ Live Campus Shuttle & Vacancy Radar")
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Fleet", f"{len(db['shuttles'])} Shuttles")
        c2.metric("Your Identity", user_email)
        c3.metric("Cloud Connection", "🟢 Active Sync")
        
        shuttles_df = pd.DataFrame(db["shuttles"])
        st.map(shuttles_df, latitude="lat", longitude="lon", size=25, zoom=15)
        
        st.divider()
        st.subheader("🙋 Smart Crowd Ping (Demand Voting)")
        st.caption("Tap your location to notify nearby drivers where passenger crowds are waiting:")
        cp_col1, cp_col2 = st.columns([2, 1])
        with cp_col1:
            ping_loc = st.selectbox("Select Your Current Hub Location:", list(db["demand_pings"].keys()))
        with cp_col2:
            st.write("")
            st.write("")
            if st.button("📍 I'm Waiting Here! (Vote Pickup Demand)", type="primary", use_container_width=True):
                db["demand_pings"][ping_loc] += 1
                st.success(f"Demand Ping recorded for **{ping_loc}**! Nearby drivers alerted on heatmap.")
                st.rerun()

        st.write("#### 🚌 Real-Time Shuttle Telemetry Stream")
        st.dataframe(shuttles_df[["Vehicle", "Status", "Vacant_Seats", "Speed", "Driver_Email", "Last_Sync"]], use_container_width=True, hide_index=True)

    # TAB 2: P2P RENTALS
    with t2:
        st.subheader("🛵 Short-Term Vehicle Rentals")
        
        with st.expander("➕ List Your Vehicle for Rent"):
            col1, col2 = st.columns(2)
            v_mod = col1.text_input("Vehicle Model", key="add_mod")
            v_rat = col1.number_input("Rate (₹/hr)", min_value=5, value=10, key="add_rat")
            v_loc = col2.text_input("Pickup Location", key="add_loc")
            v_typ = col2.selectbox("Type", ["Bicycle", "Scooty", "Motorbike", "E-Cycle"], key="add_typ")
            v_sec = st.selectbox("Security Hold Requirement", ["Student ID", "Hostel ID", "₹200 Deposit", "₹500 Deposit"], key="add_sec")
            if st.button("Publish Listing", type="primary"):
                if v_mod and v_loc:
                    db["vehicles"].append({
                        "id": f"RNT-{len(db['vehicles'])+101}",
                        "model": v_mod, "type": v_typ, "rate": v_rat,
                        "location": v_loc, "security": v_sec, "owner": user_email, "status": "Available"
                    })
                    st.success("Listed across live platform!")
                    st.rerun()

        st.write("### Available Vehicles")
        avail = [v for v in db["vehicles"] if v["status"] == "Available"]
        cols = st.columns(2)
        for idx, v in enumerate(avail):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="custom-card">
                    <h4>🚲 {v['model']} ({v['type']})</h4>
                    <p><b>Rate:</b> ₹{v['rate']}/hr | <b>Location:</b> {v['location']}</p>
                    <p><b>Owner:</b> {v['owner']}</p>
                    <span class="badge">🔒 Required Security: {v['security']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔑 Reserve Vehicle", key=f"res_{v['id']}", use_container_width=True):
                    reservation_modal(v)

        st.divider()
        st.subheader("📋 Active Rentals: Pre/Post Inspection & Security Management")
        
        if not db["active_rentals"]:
            st.info("No active rentals currently in cloud memory. Reserve a vehicle above to test live inspection logs!")
        
        for bk in db["active_rentals"]:
            v = bk["vehicle"]
            with st.expander(f"🔑 Active Booking: `{bk['booking_id']}` — {v['model']}", expanded=True):
                st.markdown(f"**Owner:** {v['owner']} | **Renter Phone:** {bk['phone']} | **Duration:** {bk['duration']} hrs")
                st.info(f"🔒 **Security Hold Verification:** `{v['security']}` (Verified prior to key handover)")
                
                c_pre, c_post = st.columns(2)
                
                with c_pre:
                    st.markdown("#### 📸 1. Pre-Rental Inspection (Pickup)")
                    pre_photo = st.file_uploader("Upload Pickup Photo", type=["jpg", "png", "jpeg"], key=f"pre_pic_{bk['booking_id']}")
                    if pre_photo:
                        bk["before_photo"] = pre_photo
                        st.image(pre_photo, caption="Pickup Inspection Photo", use_container_width=True)
                    pre_notes = st.text_area("Pre-existing Scratches / Notes", placeholder="e.g. Minor scratch on rear mudguard", key=f"pre_note_{bk['booking_id']}")
                    bk["pre_notes"] = pre_notes

                with c_post:
                    st.markdown("#### 📸 2. Post-Rental Inspection (Return)")
                    post_photo = st.file_uploader("Upload Return Photo", type=["jpg", "png", "jpeg"], key=f"post_pic_{bk['booking_id']}")
                    if post_photo:
                        bk["after_photo"] = post_photo
                        st.image(post_photo, caption="Return Inspection Photo", use_container_width=True)
                    post_notes = st.text_area("Return Condition / Damage Check", placeholder="e.g. Returned clean with zero damage", key=f"post_note_{bk['booking_id']}")
                    bk["post_notes"] = post_notes

                st.markdown("---")
                col_pay, col_sec_rel = st.columns(2)
                with col_pay:
                    pay = st.selectbox("Payment Status", ["Pending", "Paid UPI", "Paid Cash"], key=f"p_{bk['booking_id']}")
                    bk["payment_status"] = pay
                with col_sec_rel:
                    sec_released = st.checkbox("✅ Security Hold Released (ID / Deposit Returned)", key=f"sec_rel_{bk['booking_id']}")

                if st.button("🏁 Finalize Trip & Return Vehicle", key=f"c_{bk['booking_id']}", type="primary", use_container_width=True):
                    if not sec_released:
                        st.warning("Please verify and check 'Security Hold Released' before returning the vehicle!")
                    else:
                        v["status"] = "Available"
                        db["active_rentals"].remove(bk)
                        st.success("Trip finalized! Security hold released and vehicle returned to available fleet.")
                        st.rerun()

    # TAB 3: HOP-ON SHARING
    with t3:
        st.subheader("🚗 Hop-On Campus Ride Sharing")
        
        with st.expander("🚗 Offer a Hop-On Ride"):
            col1, col2 = st.columns(2)
            rf = col1.text_input("From", key="r_from")
            rt = col1.text_input("To", key="r_to")
            rv = col1.text_input("Vehicle", key="r_veh")
            rtime = col2.text_input("Departure Time", key="r_time")
            rsea = col2.number_input("Seats", min_value=1, max_value=4, value=1, key="r_seats")
            rcon = col2.text_input("Contact", key="r_con")
            if st.button("Offer Ride", type="primary"):
                if rf and rt and rcon:
                    db["rides"].append({
                        "id": f"RIDE-{len(db['rides'])+1}",
                        "driver": user_email, "from_loc": rf, "to_loc": rt,
                        "time": rtime, "seats": int(rsea), "vehicle": rv or "Personal", "contact": rcon
                    })
                    st.success("Ride Offered across live database!")
                    st.rerun()

        st.write("### Active Rides")
        rcols = st.columns(2)
        for idx, r in enumerate(db["rides"]):
            with rcols[idx % 2]:
                st.markdown(f"""
                <div class="custom-card">
                    <h4>🚗 {r['from_loc']} ➔ {r['to_loc']}</h4>
                    <p>Departure: {r['time']} | Vehicle: {r['vehicle']}</p>
                    <p>Driver: {r['driver']}</p>
                    <span class="badge">Seats Available: {r['seats']}</span>
                </div>
                """, unsafe_allow_html=True)
                if r["seats"] > 0:
                    if st.button("🤝 Hop-On", key=f"hop_{r['id']}", use_container_width=True):
                        hopon_modal(r)
                else:
                    st.button("Full", key=f"full_{r['id']}", disabled=True, use_container_width=True)

    # TAB 4: VEHICLE & TRANSIT MARKETPLACE
    with t4:
        st.subheader("🚲 Vehicle & Transit Marketplace")
        
        with st.expander("🚲 Post Secondhand Item for Sale"):
            col1, col2 = st.columns(2)
            mt = col1.text_input("Item Title", placeholder="e.g. Firefox Gear Cycle", key="m_title")
            mc = col1.selectbox("Category", ["Bicycles", "Scooters", "Accessories"], key="m_cat")
            mp = col1.number_input("Price (₹)", min_value=100, value=1000, key="m_price")
            mcon = col2.selectbox("Condition", ["Brand New", "Like New", "Good", "Fair"], key="m_cond")
            mloc = col2.text_input("Location", placeholder="e.g. Hostel 2 Bike Rack", key="m_loc")
            
            m_photo = st.file_uploader("📷 Upload Item Photo", type=["jpg", "png", "jpeg"], key="m_photo")

            if st.button("Post Item to Marketplace", type="primary"):
                if mt and mloc:
                    db["market_items"].append({
                        "id": f"MKT-{len(db['market_items'])+1}",
                        "title": mt, "category": mc, "price": mp,
                        "seller": user_email, "condition": mcon, "location": mloc,
                        "image": m_photo if m_photo else "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500"
                    })
                    st.success("Item posted live!")
                    st.rerun()

        st.write("### 🛍 Browse Secondhand Items For Sale")
        mcols = st.columns(2)
        for idx, item in enumerate(db["market_items"]):
            with mcols[idx % 2]:
                with st.container():
                    if item.get("image"):
                        st.image(item["image"], use_container_width=True)
                    
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4>🚲 {item['title']}</h4>
                        <p>💵 <b>Price:</b> ₹{item['price']} | 🏷️ <b>Category:</b> {item['category']}</p>
                        <p>✨ <b>Condition:</b> {item['condition']} | 📍 <b>Pickup:</b> {item['location']}</p>
                        <p>👤 <b>Seller:</b> {item['seller']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("💬 Contact Seller", key=f"mkt_{item['id']}", use_container_width=True):
                        st.info(f"Reach out directly via email to: **{item['seller']}**")
