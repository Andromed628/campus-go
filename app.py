import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM GLASSMORPHISM STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Campus Go | P2P Mobility & Rentals",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Glassmorphism Theme
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #e6edf3;
    }
    
    /* Header Gradient Text */
    .title-text {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .subtitle-text {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    /* Custom Card Containers */
    .vehicle-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .vehicle-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    /* Badges */
    .badge-security {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-status-paid {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-status-pending {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Tab Custom Navigation Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0d1117;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #21262d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        color: #8b949e;
        font-weight: 600;
        padding: 0px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE INITIALIZATION (PERSISTENT MEMORY)
# -----------------------------------------------------------------------------
if "vehicles" not in st.session_state:
    st.session_state.vehicles = [
        {
            "id": "RNT-101",
            "model": "Hero Hawk 21-Speed",
            "type": "Bicycle",
            "rate": 10,
            "location": "Hostel 3 Rack",
            "security": "Student ID Card",
            "owner": "student@cup.edu.in",
            "status": "Available"
        },
        {
            "id": "RNT-102",
            "model": "TVS Jupiter 125",
            "type": "Scooty",
            "rate": 35,
            "location": "Main Gate Parking",
            "security": "₹500 Cash Deposit + Hostel ID",
            "owner": "rahul@cup.edu.in",
            "status": "Available"
        }
    ]

if "active_rentals" not in st.session_state:
    st.session_state.active_rentals = []

# -----------------------------------------------------------------------------
# 3. DIALOG / POP-UP MODAL FOR RESERVATIONS (PREVENTS DISAPPEARING BUG)
# -----------------------------------------------------------------------------
@st.dialog("⚡ Confirm Vehicle Reservation")
def reservation_modal(vehicle):
    st.write(f"### **{vehicle['model']}** ({vehicle['type']})")
    st.write(f"💵 **Rate:** ₹{vehicle['rate']}/hr")
    st.write(f"🔒 **Required Security Hold:** `{vehicle['security']}`")
    st.write(f"📍 **Pickup Location:** {vehicle['location']}")
    st.write(f"👤 **Owner:** {vehicle['owner']}")
    
    st.divider()
    renter_phone = st.text_input("Mobile Number for Contact", placeholder="+91 XXXXX XXXXX")
    duration = st.text_input("Expected Rental Duration (Hours)", value="2")
    
    if st.button("🚀 Confirm Booking", use_container_width=True, type="primary"):
        if not renter_phone:
            st.error("Please provide your mobile number.")
        else:
            vehicle["status"] = "Reserved"
            st.session_state.active_rentals.append({
                "booking_id": f"BK-{vehicle['id']}",
                "vehicle": vehicle,
                "renter_phone": renter_phone,
                "duration": duration,
                "payment_status": "⏳ Pending Payment",
                "before_photo": None,
                "after_photo": None
            })
            st.success("🎉 Vehicle Reserved Successfully!")
            st.rerun()

# -----------------------------------------------------------------------------
# 4. SIDEBAR CONTROL PANEL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/26e07f/garage.png", width=60)
    st.title("Control Panel")
    
    user_email = st.text_input("Current User Email", value="student@cup.edu.in")
    st.session_state["user_email"] = user_email
    
    st.divider()
    interface_mode = st.radio(
        "Select Interface Mode",
        ["🚩 Student View", "🛠️ Driver Duty Mode"],
        index=0
    )
    
    st.info("💡 **Campus Go Tip:** Make sure to upload pre-rental condition photos before handing over vehicle keys!")

# -----------------------------------------------------------------------------
# 5. MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown('<div class="title-text">Campus Go</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Unified Campus Mobility & P2P Marketplace • Central University of Punjab</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab_radar, tab_rentals, tab_sharing, tab_market = st.tabs([
    "🛰️ Live Transit Radar",
    "🛵 P2P Rentals & Inspection",
    "🚗 Hop-On Sharing",
    "🛒 Marketplace"
])

# -----------------------------------------------------------------------------
# 6. TAB 1: LIVE TRANSIT RADAR (INTERACTIVE GPS MAP)
# -----------------------------------------------------------------------------
with tab_radar:
    st.write("## 🛰️ Live Campus Transit Radar")

    # Metrics Bar
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Fleet", "3 Shuttles")
    m2.metric("Next Pickup", "~2 Mins (Hostel 3)")
    m3.metric("GPS Connection", "🟢 Live Sync")

    st.divider()

    # Coordinates centered around Central University of Punjab (Bathinda campus)
    shuttle_data = pd.DataFrame([
        {
            "Vehicle": "⚡ E-Cart #1 (Hostel Shuttle)",
            "lat": 30.1553,
            "lon": 74.9387,
            "Status": "Moving -> Academic Block",
            "Speed": "14 km/h"
        },
        {
            "Vehicle": "⚡ E-Cart #2 (Library Line)",
            "lat": 30.1538,
            "lon": 74.9365,
            "Status": "Boarding at Hostel 3",
            "Speed": "0 km/h"
        },
        {
            "Vehicle": "🚌 Main Gate Express Shuttle",
            "lat": 30.1570,
            "lon": 74.9405,
            "Status": "Arriving Main Gate",
            "Speed": "18 km/h"
        }
    ])

    # Interactive Map Display
    st.write("### 📍 Live Fleet Map")
    st.map(
        shuttle_data,
        latitude="lat",
        longitude="lon",
        size=30,
        color="#38bdf8",
        zoom=15
    )

    # Live Fleet Status Table
    st.write("### 🚌 Active Carts & Shuttles Status")
    st.dataframe(
        shuttle_data[["Vehicle", "Status", "Speed"]],
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# 7. TAB 2: P2P RENTALS & INSPECTION HUB
# -----------------------------------------------------------------------------
with tab_rentals:
    st.write("## 🛵 Short-Term Vehicle Rentals")

    # Metrics Display
    m1, m2, m3 = st.columns(3)
    available_count = len([v for v in st.session_state.vehicles if v['status'] == 'Available'])
    m1.metric("Available Vehicles", f"{available_count} Active")
    m2.metric("Active Bookings", f"{len(st.session_state.active_rentals)} Vehicles")
    m3.metric("Platform Security", "ID / Deposit Verified")

    st.divider()

    # --- LIST A VEHICLE FOR RENT ---
    with st.expander("➕ **List Your Vehicle for Rent**", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            v_model = st.text_input("Vehicle Model", placeholder="e.g. Hero Hawk 21-Speed / Honda Activa")
            v_rate = st.number_input("Rate (₹/hr)", min_value=5, value=10, step=5)
            v_location = st.text_input("Pickup Location", placeholder="e.g. Hostel 3 Rack / Academic Block")
            
        with col2:
            v_type = st.selectbox("Vehicle Type", ["Bicycle", "Scooty", "Motorbike", "E-Cycle"])
            v_security = st.selectbox(
                "Required Security Deposit / Hold",
                [
                    "Student ID Card",
                    "Hostel ID Card",
                    "₹200 Refundable Cash Deposit",
                    "₹500 Refundable Cash Deposit",
                    "Aadhaar / Driving License Hold",
                    "None"
                ]
            )
        
        if st.button("Publish Rental Listing", type="primary"):
            if v_model and v_location:
                new_item = {
                    "id": f"RNT-{len(st.session_state.vehicles)+101}",
                    "model": v_model,
                    "type": v_type,
                    "rate": v_rate,
                    "location": v_location,
                    "security": v_security,
                    "owner": user_email,
                    "status": "Available"
                }
                st.session_state.vehicles.append(new_item)
                st.success("✨ Vehicle listed successfully!")
                st.rerun()
            else:
                st.error("Please enter the Vehicle Model and Pickup Location.")

    st.write("### 🚲 Available Vehicles for Rent")
    
    # Filter available vehicles
    available_list = [v for v in st.session_state.vehicles if v["status"] == "Available"]

    if not available_list:
        st.info("No vehicles available right now. List your vehicle above!")
    else:
        # Display as a responsive 2-column card grid
        cols = st.columns(2)
        for idx, vehicle in enumerate(available_list):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="vehicle-card">
                    <h4>🚲 {vehicle['model']} <span style="font-size:0.8rem; color:#8b949e;">({vehicle['type']})</span></h4>
                    <p><b>Rate:</b> ₹{vehicle['rate']}/hr &nbsp;|&nbsp; <b>Location:</b> {vehicle['location']}</p>
                    <p>👤 <b>Owner:</b> <span style="color:#58a6ff;">{vehicle['owner']}</span></p>
                    <p><span class="badge-security">🔒 Security Hold: {vehicle['security']}</span></p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🔑 Reserve Vehicle", key=f"res_{vehicle['id']}", use_container_width=True):
                    reservation_modal(vehicle)

    st.divider()

    # --- ACTIVE BOOKINGS & SECURITY INSPECTIONS ---
    st.write("### 📋 Active Bookings & Pre/Post Inspection Hub")

    if not st.session_state.active_rentals:
        st.caption("No active rentals currently in progress.")
    else:
        for booking in st.session_state.active_rentals:
            veh = booking["vehicle"]
            with st.container():
                st.markdown(f"#### 🔐 Rental Order: `{booking['booking_id']}` — {veh['model']}")
                
                b_col1, b_col2, b_col3 = st.columns([1, 1, 1])

                # 1. BEFORE-RENT PHOTO
                with b_col1:
                    st.write("**1. Pre-Rental Security Photo**")
                    up_before = st.file_uploader(
                        "Upload photo BEFORE handoff:",
                        type=["jpg", "png", "jpeg"],
                        key=f"before_{booking['booking_id']}"
                    )
                    if up_before:
                        booking["before_photo"] = up_before
                        st.image(up_before, caption="Pre-Rental Inspection Logged", use_container_width=True)
                        st.success("Pre-inspection logged!")

                # 2. PAYMENT TRACKER STATUS
                with b_col2:
                    st.write("**2. Rent Payment Tracker**")
                    pay_state = st.selectbox(
                        "Update Payment Status:",
                        ["⏳ Pending Payment", "✅ Paid via UPI / Online", "💵 Paid via Cash"],
                        key=f"pay_{booking['booking_id']}"
                    )
                    booking["payment_status"] = pay_state
                    
                    if "Paid" in pay_state:
                        st.markdown(f'<span class="badge-status-paid">{pay_state}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-status-pending">{pay_state}</span>', unsafe_allow_html=True)

                # 3. AFTER-RENT PHOTO
                with b_col3:
                    st.write("**3. Post-Rental Return Photo**")
                    up_after = st.file_uploader(
                        "Upload photo AFTER return:",
                        type=["jpg", "png", "jpeg"],
                        key=f"after_{booking['booking_id']}"
                    )
                    if up_after:
                        booking["after_photo"] = up_after
                        st.image(up_after, caption="Post-Rental Inspection Logged", use_container_width=True)
                        st.info("Post-inspection logged!")

                st.write("")
                # Complete Order Button with Validation Checks
                if st.button("🏁 Complete Trip & Release Hold", key=f"close_{booking['booking_id']}", type="primary"):
                    if not booking["before_photo"]:
                        st.warning("⚠️ Please upload a 'Before Rent' inspection photo first.")
                    elif "Pending" in booking["payment_status"]:
                        st.warning("⚠️ Please mark payment as completed before closing the rental.")
                    else:
                        veh["status"] = "Available"
                        st.session_state.active_rentals.remove(booking)
                        st.balloons()
                        st.success(f"Trip {booking['booking_id']} successfully completed!")
                        st.rerun()

            st.divider()

# -----------------------------------------------------------------------------
# 8. TAB 3 & 4: HOP-ON SHARING & MARKETPLACE
# -----------------------------------------------------------------------------
with tab_sharing:
    st.write("## 🚗 Hop-On Campus Ride Sharing")
    st.info("Peer-to-peer ride pooling and campus hop-on requests will render here.")

with tab_market:
    st.write("## 🛒 Student Marketplace")
    st.info("Buy & sell second-hand study material, mattresses, and campus gear.")

