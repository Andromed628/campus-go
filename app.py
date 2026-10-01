import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. PAGE CONFIG & STYLING
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
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# --------------------------------------------------
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
        {"id": "MKT-1", "title": "Hercules Roadeo MTB", "category": "Bicycles", "price": 2400, "seller": "sneha@cup.edu.in", "condition": "Good", "location": "Hostel 2"},
        {"id": "MKT-2", "title": "TVS Wego 110cc", "category": "Scooters", "price": 18500, "seller": "amit@cup.edu.in", "condition": "Well Maintained", "location": "Hostel 1"},
        {"id": "MKT-3", "title": "Studds Helmet (M)", "category": "Accessories", "price": 550, "seller": "vikram@cup.edu.in", "condition": "Like New", "location": "Hostel 3"}
    ]

# --------------------------------------------------
# 3. MODAL DIALOGS
# --------------------------------------------------
@st.dialog("⚡ Confirm Vehicle Reservation")
def reservation_modal(v):
    st.write(f"### {v['model']} ({v['type']})")
    st.write(f"💵 Rate: ₹{v['rate']}/hr | 📍 Location: {v['location']}")
    st.write(f"🔒 Security Hold: `{v['security']}`")
    phone = st.text_input("Mobile Number")
    duration = st.text_input("Duration (Hours)", value="2")
    if st.button("🚀 Confirm Booking", type="primary", use_container_width=True):
        if phone:
            v["status"] = "Reserved"
            st.session_state.active_rentals.append({
                "booking_id": f"BK-{v['id']}",
                "vehicle": v,
                "phone": phone,
                "duration": duration,
                "payment_status": "Pending",
                "before_photo": None
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
# 4. SIDEBAR & HEADER
# --------------------------------------------------
with st.sidebar:
    st.title("🧭 Navigo Control")
    user_email = st.text_input("User Email", value="student@cup.edu.in")

st.markdown('<div class="title-text">Navigo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Campus Mobility & Vehicle Marketplace • Central University of Punjab</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🛰️ Live Radar", "🛵 P2P Rentals", "🚗 Hop-On Sharing", "🚲 Marketplace"])

# --------------------------------------------------
# 5. TAB 1: LIVE TRANSIT RADAR
# --------------------------------------------------
with t1:
    st.subheader("🛰️ Live Campus Shuttle Radar")
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Fleet", "3 Shuttles")
    c2.metric("Next Pickup", "~2 Mins")
    c3.metric("GPS Sync", "🟢 Online")
    
    shuttles = pd.DataFrame([
        {"Vehicle": "⚡ E-Cart #1", "lat": 30.1553, "lon": 74.9387, "Status": "Moving -> Academic Block"},
        {"Vehicle": "⚡ E-Cart #2", "lat": 30.1538, "lon": 74.9365, "Status": "Boarding at Hostel 3"},
        {"Vehicle": "🚌 Gate Shuttle", "lat": 30.1570, "lon": 74.9405, "Status": "Arriving Main Gate"}
    ])
    st.map(shuttles, latitude="lat", longitude="lon", size=25, zoom=15)
    st.dataframe(shuttles[["Vehicle", "Status"]], use_container_width=True, hide_index=True)

# --------------------------------------------------
# 6. TAB 2: P2P RENTALS & INSPECTION
# --------------------------------------------------
with t2:
    st.subheader("🛵 Short-Term Vehicle Rentals")
    
    with st.expander("➕ List Your Vehicle for Rent"):
        col1, col2 = st.columns(2)
        v_mod = col1.text_input("Vehicle Model", key="add_mod")
        v_rat = col1.number_input("Rate (₹/hr)", min_value=5, value=10, key="add_rat")
        v_loc = col2.text_input("Pickup Location", key="add_loc")
        v_typ = col2.selectbox("Type", ["Bicycle", "Scooty", "Motorbike", "E-Cycle"], key="add_typ")
        v_sec = st.selectbox("Security Hold", ["Student ID", "Hostel ID", "₹200 Deposit", "₹500 Deposit"], key="add_sec")
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
                <p>Rate: ₹{v['rate']}/hr | Location: {v['location']}</p>
                <p>Owner: {v['owner']}</p>
                <span class="badge">Security: {v['security']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔑 Reserve", key=f"res_{v['id']}", use_container_width=True):
                reservation_modal(v)

    st.divider()
    st.write("### 📋 Active Rentals")
    for bk in st.session_state.active_rentals:
        v = bk["vehicle"]
        st.write(f"**Booking:** `{bk['booking_id']}` - {v['model']}")
        up = st.file_uploader("Pre-rental photo", type=["jpg", "png"], key=f"up_{bk['booking_id']}")
        if up:
            bk["before_photo"] = up
            st.success("Photo logged!")
        pay = st.selectbox("Payment Status", ["Pending", "Paid UPI", "Paid Cash"], key=f"p_{bk['booking_id']}")
        bk["payment_status"] = pay
        if st.button("Complete Trip", key=f"c_{bk['booking_id']}", type="primary"):
            v["status"] = "Available"
            st.session_state.active_rentals.remove(bk)
            st.success("Completed!")
            st.rerun()

# --------------------------------------------------
# 7. TAB 3: HOP-ON RIDE SHARING
# --------------------------------------------------
with t3:
    st.subheader("🚗 Hop-On Campus Ride Sharing")
    
    with st.expander("🚗 Offer a Ride"):
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
                <span class="badge">Seats: {r['seats']}</span>
            </div>
            """, unsafe_allow_html=True)
            if r["seats"] > 0:
                if st.button("🤝 Hop-On", key=f"hop_{r['id']}", use_container_width=True):
                    hopon_modal(r)
            else:
                st.button("Full", key=f"full_{r['id']}", disabled=True, use_container_width=True)

# --------------------------------------------------
# 8. TAB 4: MARKETPLACE
# --------------------------------------------------
with t4:
    st.subheader("🚲 Vehicle & Transit Marketplace")
    
    with st.expander("🚲 Sell Vehicle / Accessory"):
        col1, col2 = st.columns(2)
        mt = col1.text_input("Item Title", key="m_title")
        mc = col1.selectbox("Category", ["Bicycles", "Scooters", "Accessories"], key="m_cat")
        mp = col1.number_input("Price (₹)", min_value=100, value=1000, key="m_price")
        mcon = col2.selectbox("Condition", ["Brand New", "Like New", "Good", "Fair"], key="m_cond")
        mloc = col2.text_input("Location", key="m_loc")
        if st.button("Post Item", type="primary"):
            if mt and mloc:
                st.session_state.market_items.append({
                    "id": f"MKT-{len(st.session_state.market_items)+1}",
                    "title": mt, "category": mc, "price": mp,
                    "seller": user_email, "condition": mcon, "location": mloc
                })
                st.success("Item Posted!")
                st.rerun()

    st.write("### For Sale")
    mcols = st.columns(2)
    for idx, item in enumerate(st.session_state.market_items):
        with mcols[idx % 2]:
            st.markdown(f"""
            <div class="custom-card">
                <h4>🚲 {item['title']}</h4>
                <p>Price: ₹{item['price']} | Category: {item['category']}</p>
                <p>Condition: {item['condition']} | Location: {item['location']}</p>
                <p>Seller: {item['seller']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💬 Contact Seller", key=f"mkt_{item['id']}", use_container_width=True):
                st.info(f"Contact seller at: {item['seller']}")
