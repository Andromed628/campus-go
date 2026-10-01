import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. PAGE CONFIG & CUSTOM STYLING
# --------------------------------------------------
st.set_page_config(
    page_title="Navigo | Campus Mobility",
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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# --------------------------------------------------
if "shuttles" not in st.session_state:
    st.session_state.shuttles = [
        {"Vehicle": "⚡ E-Cart #1 (Hostel Shuttle)", "lat": 30.1553, "lon": 74.9387, "Status": "Moving -> Academic Block", "Speed": "14 km/h"},
        {"Vehicle": "⚡ E-Cart #2 (Library Line)", "lat": 30.1538, "lon": 74.9365, "Status": "Boarding at Hostel 3", "Speed": "0 km/h"},
        {"Vehicle": "🚌 Main Gate Express", "lat": 30.1570, "lon": 74.9405, "Status": "Arriving Main Gate", "Speed": "18 km/h"}
    ]

if "vehicles" not in st.session_state:
    st.session_state.vehicles = [
        {"id": "RNT-101", "model": "Hero Hawk 21-Speed", "type": "Bicycle", "rate": 10, "location": "Hostel 3 Rack", "security": "Student ID", "owner": "student@cup.edu.in", "status": "Available"},
        {"id": "RNT-102", "model": "TVS Jupiter 125", "type": "Scooty", "rate": 35, "location": "Main Gate", "security": "₹500 Deposit", "owner": "rahul@cup.edu.in", "status": "Available"}
    ]

if "active_rentals" not in st.session_state:
    st.session_state.active_rentals = []

if "rides" not in st.session_state:
    st.session_state.rides = [
        {"id": "RIDE-1", "driver": "rahul@cup.edu.in", "from_loc": "Hostel 3", "to_loc": "Academic Block", "time": "09:15 AM", "seats": 2, "vehicle": "TVS Jupiter", "contact": "9876543210"},
        {"id": "RIDE-2", "driver": "priya@cup.edu.in", "from_loc": "Main Gate", "to_loc": "Library", "time": "10:30 AM", "seats": 1, "vehicle": "Electric Scooter", "contact": "9123456789"}
    ]

if "market_items" not in st.session_state:
    st.session_state.market_items = [
        {
            "id": "MKT-1", "title": "Hercules Roadeo MTB", "category": "Bicycles", 
            "price": 2400, "seller": "sneha@cup.edu.in", "condition": "Good", 
            "location": "Hostel 2", "image": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500"
        },
        {
            "id": "MKT-2", "title": "TVS Wego 110cc", "category": "Scooters", 
            "price": 18500, "seller": "amit@cup.edu.in", "condition": "Well Maintained", 
            "location": "Hostel 1", "image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500"
        },
        {
            "id": "MKT-3", "title": "Studds Helmet (Size M)", "category": "Accessories", 
            "price": 550, "seller": "vikram@cup.edu.in", "condition": "Like New", 
            "location": "Hostel 3", "image": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=500"
        }
    ]

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
            st.session_state.active_rentals.append({
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
# 4. SIDEBAR - USER & MODE SWITCHER
# --------------------------------------------------
with st.sidebar:
    st.title("🧭 Navigo Control")
    user_email = st.text_input("User Email", value="student@cup.edu.in")
    st.divider()
    interface_mode = st.radio(
        "Select Interface Mode",
        ["🧑‍🎓 Student Mode", "🛺 Driver Duty Mode"],
        index=0
    )

st.markdown('<div class="title-text">Navigo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Campus Mobility & Vehicle Marketplace • Central University of Punjab</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 5. DRIVER DUTY MODE DASHBOARD
# --------------------------------------------------
if interface_mode == "🛺 Driver Duty Mode":
    st.markdown('<span class="badge-driver">🛺 DRIVER DUTY CONTROL PANEL</span>', unsafe_allow_html=True)
    st.write("")
    st.subheader("🚌 Manage Campus Shuttle GPS & Route")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        shuttle_names = [s["Vehicle"] for s in st.session_state.shuttles]
        selected_shuttle = st.selectbox("Select Your Vehicle", shuttle_names)
        new_status = st.selectbox("Current Shuttle Status", [
            "Moving -> Academic Block",
            "Boarding at Hostel 3",
            "Boarding at Main Gate",
            "Moving -> Central Library",
            "Idle at Parking"
        ])
    
    with col_d2:
        new_speed = st.slider("Current Speed (km/h)", 0, 30, 12)
        on_duty = st.toggle("Active Duty Signal (Live GPS)", value=True)
    
    if st.button("📡 Broadcast Real-Time GPS Update", type="primary"):
        for s in st.session_state.shuttles:
            if s["Vehicle"] == selected_shuttle:
                s["Status"] = new_status
                s["Speed"] = f"{new_speed} km/h"
        st.success(f"Updated live GPS for {selected_shuttle}!")
        st.rerun()

    st.divider()
    st.subheader("📋 Active Passenger Hop-On Requests")
    st.dataframe(pd.DataFrame(st.session_state.rides), use_container_width=True, hide_index=True)

# --------------------------------------------------
# 6. STUDENT MODE DASHBOARD (4 TABS)
# --------------------------------------------------
else:
    t1, t2, t3, t4 = st.tabs(["🛰️ Live Radar", "🛵 P2P Rentals", "🚗 Hop-On Sharing", "🚲 Marketplace"])

    # TAB 1: LIVE RADAR
    with t1:
        st.subheader("🛰️ Live Campus Shuttle Radar")
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Fleet", f"{len(st.session_state.shuttles)} Shuttles")
        c2.metric("Next Pickup", "~2 Mins")
        c3.metric("GPS Sync", "🟢 Online")
        
        shuttles_df = pd.DataFrame(st.session_state.shuttles)
        st.map(shuttles_df, latitude="lat", longitude="lon", size=25, zoom=15)
        st.dataframe(shuttles_df[["Vehicle", "Status", "Speed"]], use_container_width=True, hide_index=True)

    # TAB 2: P2P RENTALS & INSPECTION / SECURITY
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
                    st.session_state.vehicles.append({
                        "id": f"RNT-{len(st.session_state.vehicles)+101}",
                        "model": v_mod, "type": v_typ, "rate": v_rat,
                        "location": v_loc, "security": v_sec, "owner": user_email, "status": "Available"
                    })
                    st.success("Listed!")
                    st.rerun()

        st.write("### Available Vehicles")
        avail = [v for v in st.session_state.vehicles if v["status"] == "Available"]
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
        
        if not st.session_state.active_rentals:
            st.info("No active rentals currently. Reserve a vehicle above to test inspection logs and security hold controls!")
        
        for bk in st.session_state.active_rentals:
            v = bk["vehicle"]
            with st.expander(f"🔑 Active Booking: `{bk['booking_id']}` — {v['model']}", expanded=True):
                st.markdown(f"**Owner:** {v['owner']} | **Renter Phone:** {bk['phone']} | **Duration:** {bk['duration']} hrs")
                
                # Security Hold Box
                st.info(f"🔒 **Security Hold Verification:** `{v['security']}` (Verified prior to key handover)")
                
                c_pre, c_post = st.columns(2)
                
                # Pre-Inspection
                with c_pre:
                    st.markdown("#### 📸 1. Pre-Rental Inspection (Pickup)")
                    pre_photo = st.file_uploader("Upload Pickup Photo", type=["jpg", "png", "jpeg"], key=f"pre_pic_{bk['booking_id']}")
                    if pre_photo:
                        bk["before_photo"] = pre_photo
                        st.image(pre_photo, caption="Pickup Inspection Photo", use_container_width=True)
                    pre_notes = st.text_area("Pre-existing Scratches / Notes", placeholder="e.g. Minor scratch on rear mudguard", key=f"pre_note_{bk['booking_id']}")
                    bk["pre_notes"] = pre_notes

                # Post-Inspection
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
                        st.session_state.active_rentals.remove(bk)
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
                    st.session_state.rides.append({
                        "id": f"RIDE-{len(st.session_state.rides)+1}",
                        "driver": user_email, "from_loc": rf, "to_loc": rt,
                        "time": rtime, "seats": int(rsea), "vehicle": rv or "Personal", "contact": rcon
                    })
                    st.success("Ride Offered!")
                    st.rerun()

        st.write("### Active Rides")
        rcols = st.columns(2)
        for idx, r in enumerate(st.session_state.rides):
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
                    st.session_state.market_items.append({
                        "id": f"MKT-{len(st.session_state.market_items)+1}",
                        "title": mt, "category": mc, "price": mp,
                        "seller": user_email, "condition": mcon, "location": mloc,
                        "image": m_photo if m_photo else "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=500"
                    })
                    st.success("Item posted successfully with photo!")
                    st.rerun()

        st.write("### 🛍️ Browse Secondhand Items For Sale")
        mcols = st.columns(2)
        for idx, item in enumerate(st.session_state.market_items):
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
