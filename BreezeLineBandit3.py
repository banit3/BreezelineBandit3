import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set Page Configuration to match Breezeline branding
st.set_page_config(
    page_title="Breezeline Kiosk Portal - Darius/banit3 Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Shared File for Leads Database
LEADS_FILE = 'kiosk_leads.csv'

# Define Breezeline Brand Colors & Responsive Modern Styling
st.markdown("""
<style>
    /* Global Base Page Styling */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* Top Banner Styling matching Breezeline Brand colors */
    .title-banner {
        background: linear-gradient(135deg, #002d62 0%, #0076a3 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        border-bottom: 5px solid #4dc3e6;
    }
    
    /* Elegant CSS Pinwheel logo */
    .brand-pinwheel {
        display: inline-block;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: conic-gradient(
            #002d62 0deg 72deg, 
            #005a9c 72deg 144deg, 
            #0076a3 144deg 216deg, 
            #4dc3e6 216deg 288deg, 
            #b1e4f3 288deg 360deg
        );
        margin-bottom: 8px;
        animation: spin 8s linear infinite;
    }
    
    @keyframes spin {
        100% { transform: rotate(360deg); }
    }
    
    /* Custom CSS Cards for visual layout */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #0076a3;
        margin-bottom: 15px;
    }
    
    /* Comforting Human Pitch box styling */
    .pitch-box {
        background-color: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 18px;
        border-radius: 8px;
        margin-top: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
    }
    
    .pitch-text {
        font-size: 1.12rem;
        line-height: 1.6;
        color: #14532d !important;
        font-family: "Source Sans Pro", sans-serif;
    }
    
    .legacy-box {
        background-color: #fffbebf8;
        border-left: 5px solid #d97706;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    
    .contact-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 4px solid #002d62;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    
    .footer-credit {
        text-align: center;
        margin-top: 40px;
        padding: 18px;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Breezeline 2026 Grounded Pricing Plans
BREEZELINE_INTERNET = {
    '100': {'name': 'Internet 100', 'speed': '100 Mbps', 'price': 20.00, 'lock': '2 Years (24 Mo)', 'equipment': 'Included Free for 24 Months', 'gift_card': 0},
    '200': {'name': 'Internet 200', 'speed': '200 Mbps', 'price': 30.00, 'lock': '2 Years (24 Mo)', 'equipment': 'Included Free for 24 Months', 'gift_card': 50},
    '500': {'name': 'Internet 500', 'speed': '500 Mbps', 'price': 40.00, 'lock': '5 Years (60 Mo)', 'equipment': 'Included Free for 60 Months', 'gift_card': 100, 'mobile_promo': 'Free 1st Line for 12 Months'},
    '1000': {'name': '1 Gig', 'speed': '1000 Mbps', 'price': 45.00, 'lock': '5 Years (60 Mo)', 'equipment': 'Included Free for 60 Months', 'gift_card': 100, 'mobile_promo': 'Free 1st Line for 12 Months'}
}

BREEZELINE_MOBILE_LINE_RATE = 35.00  # Standard Unlimited line $35/mo
BREEZELINE_STREAM_TV_RATE = 20.00    # Stream TV Everyday Favorites $20/mo

# Cumberland MD Area Competitor & Legacy Pricing Data
COMPETITOR_DATA = {
    'Xfinity (Comcast - Cumberland)': {
        'internet_intro': {'300 Mbps': 40.00, '500 Mbps': 45.00, '1 Gig': 50.00},
        'internet_regular': {'300 Mbps': 75.00, '500 Mbps': 95.00, '1 Gig': 115.00},
        'mobile_per_line': 45.00,
        'tv_base': 65.00
    },
    'AT&T (Internet Air / Wireless)': {
        'internet_intro': {'Internet Air (300 Mbps)': 60.00, 'Value 2.0': 50.00, 'Extra 2.0': 70.00},
        'internet_regular': {'Internet Air (300 Mbps)': 60.00, 'Value 2.0': 50.00, 'Extra 2.0': 70.00},
        'mobile_per_line': 50.00,
        'tv_base': 85.00
    },
    'Verizon (5G Home / Fios)': {
        'internet_intro': {'300 Mbps': 50.00, '500 Mbps': 70.00, '1 Gig': 90.00},
        'internet_regular': {'300 Mbps': 50.00, '500 Mbps': 70.00, '1 Gig': 90.00},
        'mobile_per_line': 45.00,
        'tv_base': 75.00
    },
    'Old Breezeline / Atlantic Broadband (Post-Promo Regular Rates)': {
        'internet_intro': {'Legacy 100/200 Mbps': 77.00, 'Legacy 500 Mbps': 107.00, 'Legacy 1 Gig': 137.00}, # Includes $12 modem fee
        'internet_regular': {'Legacy 100/200 Mbps': 77.00, 'Legacy 500 Mbps': 107.00, 'Legacy 1 Gig': 137.00},
        'mobile_per_line': 35.00,
        'tv_base': 105.00 # Includes broadcast retransmission fees
    }
}

# CSV Lead Database Loader
def load_leads():
    columns = ['Date', 'Name', 'Phone', 'Email', 'Street Address', 'Account Number', 'PIN', 'Current Provider', 'Status', 'Notes']
    if os.path.exists(LEADS_FILE):
        try:
            df = pd.read_csv(LEADS_FILE)
            for col in columns:
                if col not in df.columns:
                    df[col] = "N/A"
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_lead(name, phone, email, address, account_num, pin, provider, status, notes):
    df = load_leads()
    new_lead = pd.DataFrame([{
        'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Name': name,
        'Phone': phone,
        'Email': email,
        'Street Address': address,
        'Account Number': account_num,
        'PIN': pin,
        'Current Provider': provider,
        'Status': status,
        'Notes': notes
    }])
    df = pd.concat([df, new_lead], ignore_index=True)
    df.to_csv(LEADS_FILE, index=False)

# Sidebar Quick Reference Hub
st.sidebar.markdown('<div style="text-align: center;"><div class="brand-pinwheel"></div></div>', unsafe_allow_html=True)
st.sidebar.title("☎️ Kiosk Quick Reference")
st.sidebar.write("Crucial directory & links for Cumberland Mall kiosk staff.")

st.sidebar.markdown("""
<div class="contact-card">
    <strong style="color: #002d62;">Sales Line</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">833-694-6189</span>
</div>
<div class="contact-card">
    <strong style="color: #002d62;">New Customer Line</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">844-495-3128</span>
</div>
<div class="contact-card">
    <strong style="color: #002d62;">Old Customer Support (Care/Billing)</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">866-731-6393</span>
</div>
<div class="contact-card">
    <strong style="color: #002d62;">I.T. & Video Tech Support</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">888-201-6375</span>
</div>
<div class="contact-card">
    <strong style="color: #002d62;">Device Activation Line</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">855-214-6014</span>
</div>
<div class="contact-card">
    <strong style="color: #002d62;">Mobile Sales Line</strong><br>
    <span style="font-size: 1.1rem; font-weight: bold; color: #0076a3;">855-811-5188</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.info("📦 **Equipment Return Portal**\n\nDirect link for customers returning modems or boxes:\n\n**breezeline.shipment.co**")

st.sidebar.markdown("""
<div style="text-align: center; margin-top: 25px; font-size: 0.8rem; color: #94a3b8;">
    Compiled & Customized for Kiosk Staff by<br>
    <strong style="color: #002d62;">Darius/banit3</strong>
</div>
""", unsafe_allow_html=True)

# Main Banner Header
st.markdown('<div class="title-banner"><div class="brand-pinwheel"></div><h1>⚡ Breezeline Kiosk Sales Portal ⚡</h1><p>Instant standalone calculators, old/new pricing audit, and lead logger</p></div>', unsafe_allow_html=True)

# Main App Navigation Tabs
tab_nav1, tab_nav2, tab_nav3 = st.tabs([
    "🧮 Standalone Savings Calculators", 
    "✍️ Log Customer Interaction", 
    "📈 Kiosk Performance Dashboard"
])

# ==================== TAB 1: STANDALONE CALCULATORS ====================
with tab_nav1:
    st.header("Select Specific Calculation Mode")
    st.write("You can calculate individual savings for **Internet Only**, **Mobile Only**, **TV Only**, or run a **Full Triple-Play Bundle Comparison**:")

    calc_mode = st.radio(
        "Choose Category:", 
        ["🌐 Internet Savings Calculator", "📱 Mobile Savings Calculator", "📺 TV Savings Calculator", "⚡ Full Bundle Calculator"],
        horizontal=True
    )
    st.markdown("---")

    # 1. INTERNET ONLY CALCULATOR
    if calc_mode == "🌐 Internet Savings Calculator":
        st.subheader("🌐 Standalone Internet Savings Calculator")
        st.write("Compare their current home internet bill against Breezeline's 2-year and 5-year price locked plans:")

        c1, c2 = st.columns(2)
        with c1:
            prov = st.selectbox("Current Provider", ["Xfinity (Comcast - Cumberland)", "AT&T (Internet Air / Wireless)", "Verizon (5G Home / Fios)", "Old Breezeline / Atlantic Broadband (Post-Promo Regular Rates)", "Custom / Other"])
            
            if prov != "Custom / Other":
                tiers = list(COMPETITOR_DATA[prov]['internet_intro'].keys())
                selected_tier = st.selectbox("Current Speed / Plan Tier", tiers)
                is_post_promo = st.checkbox("Has their 12 month promotional rate expired? (Check year 2 price hike)", value=(prov.startswith("Old Breezeline")))
                
                if is_post_promo and prov in COMPETITOR_DATA:
                    default_cost = COMPETITOR_DATA[prov]['internet_regular'][selected_tier]
                    st.caption("ℹ️ Showing post promotional regular rate (includes modem rental fees where applicable).")
                else:
                    default_cost = COMPETITOR_DATA[prov]['internet_intro'][selected_tier]
                    
                current_internet_bill = st.number_input("Monthly Internet Bill ($)", value=float(default_cost), step=1.0)
                speed_num = 300 if "300" in selected_tier or "100" in selected_tier or "Air" in selected_tier else (500 if "500" in selected_tier else 1000)
            else:
                speed_num = st.number_input("Current Speed (Mbps)", value=300, step=50)
                current_internet_bill = st.number_input("Monthly Internet Bill ($)", value=75.00, step=1.0)

        # Match Breezeline Internet Plan
        if speed_num <= 100: bz_key = '100'
        elif speed_num <= 200: bz_key = '200'
        elif speed_num <= 500: bz_key = '500'
        else: bz_key = '1000'
        
        bz_plan = BREEZELINE_INTERNET[bz_key]
        bz_cost = bz_plan['price']
        m_save = current_internet_bill - bz_cost
        two_yr_save = (m_save * 24) + bz_plan['gift_card']

        with c2:
            st.subheader("Breezeline Recommended Internet Plan")
            st.success(f"**{bz_plan['name']} ({bz_plan['speed']}) @ ${bz_cost:.2f}/mo**")
            st.write(f"• **Price Guarantee:** Locked for {bz_plan['lock']}")
            st.write(f"• **Hardware Fee:** {bz_plan['equipment']} ($0 rental fee)")
            if bz_plan['gift_card'] > 0:
                st.write(f"• **Switching Promo:** ${bz_plan['gift_card']} Prepaid Visa Gift Card")

        if m_save > 0:
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Monthly Internet Savings", f"${m_save:.2f}/mo")
            mc2.metric("2-Year Total Saved Value", f"${two_yr_save:.2f}")
            mc3.metric("Breezeline Rate", f"${bz_cost:.2f}/mo")

            st.markdown(f"""
            <div class="pitch-box">
                <h3 style="margin-top:0; color: #14532d;">🎤 Human Spoken Pitch (Internet Only):</h3>
                <p class="pitch-text">
                    "Hey, I completely understand where you are coming from. Most providers like Comcast or old Atlantic Broadband plans hit you with a massive thirty to fifty dollar price jump after year one, plus ten to fifteen dollars a month just to rent their modem modem box. With Breezeline, we will lock in your internet rate at just <strong>${bz_cost:.2f} a month</strong> for <strong>{bz_plan['lock']}</strong>. We include your equipment completely free, there are no contracts, and you keep an extra <strong>${m_save:.2f} in your pocket every single month</strong>. Over two years, that puts <strong>${two_yr_save:.2f}</strong> back in your wallet. Let us handle the setup risk free."
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("They are on a heavy introductory discount. Emphasize zero equipment rental fees, no annual contracts, and multi year price lock guarantee!")

    # 2. MOBILE ONLY CALCULATOR
    elif calc_mode == "📱 Mobile Savings Calculator":
        st.subheader("📱 Standalone Mobile Savings Calculator")
        st.write("Compare their current wireless phone bill against Breezeline Unlimited Mobile ($35/line):")

        c1, c2 = st.columns(2)
        with c1:
            mobile_carrier = st.selectbox("Current Mobile Carrier", ["Xfinity Mobile ($45/line)", "AT&T Wireless ($50/line)", "Verizon Wireless ($45/line)", "Custom / Other Carrier"])
            num_lines = st.number_input("Number of Mobile Lines", min_value=1, max_value=10, value=2, step=1)
            
            if "Xfinity" in mobile_carrier or "Verizon" in mobile_carrier:
                default_line_rate = 45.00
            elif "AT&T" in mobile_carrier:
                default_line_rate = 50.00
            else:
                default_line_rate = 45.00
                
            current_mobile_total = st.number_input("Current Total Monthly Mobile Bill ($)", value=float(default_line_rate * num_lines), step=5.0)

        # Breezeline Mobile Math
        bz_mobile_total = BREEZELINE_MOBILE_LINE_RATE * num_lines
        m_mobile_save = current_mobile_total - bz_mobile_total
        two_yr_mobile_save = m_mobile_save * 24

        with c2:
            st.subheader("Breezeline Unlimited Mobile Setup")
            st.info(f"**Breezeline Unlimited Mobile:** ${BREEZELINE_MOBILE_LINE_RATE:.2f}/mo per line")
            st.write(f"• **Lines Configured:** {num_lines} Line(s)")
            st.write(f"• **Breezeline Monthly Total:** **${bz_mobile_total:.2f}/mo**")
            st.write("• **Features:** Unlimited Talk, Text, & High-Speed 5G Data")
            st.write("• **Flexibility:** No annual contract, bring your own unlocked phones")

        if m_mobile_save > 0:
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Monthly Mobile Savings", f"${m_mobile_save:.2f}/mo")
            mc2.metric("2-Year Wireless Savings", f"${two_yr_mobile_save:.2f}")
            mc3.metric("Breezeline Mobile Rate", f"${bz_mobile_total:.2f}/mo")

            st.markdown(f"""
            <div class="pitch-box">
                <h3 style="margin-top:0; color: #14532d;">🎤 Human Spoken Pitch (Mobile Only):</h3>
                <p class="pitch-text">
                    "If you bring your {num_lines} phone line{'s' if num_lines > 1 else ''} over to Breezeline Unlimited Mobile, your rate is just thirty five dollars per line. You get the exact same nationwide high speed coverage, but you cut your mobile bill down to <strong>${bz_mobile_total:.2f} a month</strong>. That saves you <strong>${m_mobile_save:.2f} every month</strong>, which is over <strong>${two_yr_mobile_save:.2f} in real savings</strong> over the next two years. You keep your exact same phone numbers and devices without signing any long term contracts."
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("They currently have a heavily discounted family rate. Mention that existing Breezeline 500 Mbps and 1 Gig internet plans include a **Free Unlimited Mobile line for 12 months**!")

    # 3. TV ONLY CALCULATOR
    elif calc_mode == "📺 TV Savings Calculator":
        st.subheader("📺 Standalone TV & Video Savings Calculator")
        st.write("Compare high cable or satellite TV bills against Breezeline Stream TV or DIRECTV:")

        c1, c2 = st.columns(2)
        with c1:
            tv_provider = st.selectbox("Current TV Service", ["Xfinity Cable TV ($65+ base + $20 fees = $85/mo)", "DirecTV / Satellite ($85+/mo)", "Legacy Atlantic Broadband / Cable TV ($85+ base + $20 retrans = $105/mo)", "Custom / Other Cable TV"])
            
            if "Atlantic" in tv_provider: default_tv_bill = 105.00
            elif "DirecTV" in tv_provider: default_tv_bill = 85.00
            elif "Xfinity" in tv_provider: default_tv_bill = 85.00
            else: default_tv_bill = 90.00
            
            current_tv_bill = st.number_input("Current Monthly TV Bill ($)", value=float(default_tv_bill), step=5.0)

        # Breezeline Stream TV Rate
        bz_tv_cost = BREEZELINE_STREAM_TV_RATE
        m_tv_save = current_tv_bill - bz_tv_cost
        two_yr_tv_save = m_tv_save * 24

        with c2:
            st.subheader("Breezeline Stream TV Solution")
            st.success(f"**Breezeline Stream TV Everyday Favorites @ ${bz_tv_cost:.2f}/mo**")
            st.write("• **Channels:** Includes local networks and everyday favorite channels")
            st.write("• **Cloud DVR:** Access live and recorded programs on compatible devices")
            st.write("• **No Heavy Box Fees:** Stream directly over home Wi-Fi")

        if m_tv_save > 0:
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Monthly TV Savings", f"${m_tv_save:.2f}/mo")
            mc2.metric("2-Year TV Savings", f"${two_yr_tv_save:.2f}")
            mc3.metric("Breezeline Stream TV Rate", f"${bz_tv_cost:.2f}/mo")

            st.markdown(f"""
            <div class="pitch-box">
                <h3 style="margin-top:0; color: #14532d;">🎤 Human Spoken Pitch (TV Only):</h3>
                <p class="pitch-text">
                    "Traditional cable TV bills are skyrocketing because of broadcast retransmission fees and box rental charges that add twenty to thirty dollars on top of your plan. With Breezeline Stream TV, you get all your essential local channels and everyday entertainment for just <strong>twenty dollars a month</strong>. That immediately saves you <strong>${m_tv_save:.2f} every single month</strong>, putting <strong>${two_yr_tv_save:.2f}</strong> back in your pocket over two years while letting you stream seamlessly on your smart TVs or devices."
                </p>
            </div>
            """, unsafe_allow_html=True)

    # 4. FULL BUNDLE CALCULATOR
    else:
        st.subheader("⚡ Full Triple-Play Bundle Calculator")
        st.write("Calculate complete savings across Internet, Mobile, and TV combined:")

        c1, c2 = st.columns(2)
        with c1:
            bundle_prov = st.selectbox("Current Provider", ["Xfinity (Comcast - Cumberland)", "AT&T (Internet Air / Wireless)", "Verizon (5G Home / Fios)", "Old Breezeline / Atlantic Broadband (Post-Promo Regular Rates)", "Custom / Other"])
            
            b_speed = st.selectbox("Current Internet Speed", ["300 Mbps", "500 Mbps", "1 Gig"])
            b_mobile_lines = st.number_input("Number of Mobile Lines", min_value=0, max_value=10, value=1, step=1)
            b_include_tv = st.checkbox("Include Cable / Stream TV in bundle?", value=True)

            if bundle_prov != "Custom / Other":
                s_key = "1000" if "1 Gig" in b_speed else ("500" if "500" in b_speed else "300")
                if s_key not in COMPETITOR_DATA[bundle_prov]['internet_intro']:
                    s_key = list(COMPETITOR_DATA[bundle_prov]['internet_intro'].keys())[0]
                else:
                    s_key = [k for k in COMPETITOR_DATA[bundle_prov]['internet_intro'].keys() if s_key in k][0]
                    
                i_cost = COMPETITOR_DATA[bundle_prov]['internet_regular'][s_key]
                m_cost = COMPETITOR_DATA[bundle_prov]['mobile_per_line'] * b_mobile_lines
                t_cost = COMPETITOR_DATA[bundle_prov]['tv_base'] if b_include_tv else 0.0
            else:
                i_cost = 75.00
                m_cost = 45.00 * b_mobile_lines
                t_cost = 85.00 if b_include_tv else 0.0

            total_comp_bundle = i_cost + m_cost + t_cost
            st.write(f"• Current Estimated Total Monthly Bill: **${total_comp_bundle:.2f}/mo**")

        # Breezeline Bundle Calculation
        if "1 Gig" in b_speed: bz_i_key = '1000'
        elif "500" in b_speed: bz_i_key = '500'
        else: bz_i_key = '200'

        bz_i_plan = BREEZELINE_INTERNET[bz_i_key]
        bz_i_price = bz_i_plan['price']
        
        # Mobile Promo Stacking: Free 1st line for 12 mos on 500+ Mbps
        if bz_i_key in ['500', '1000'] and b_mobile_lines > 0:
            bz_m_price_y1 = BREEZELINE_MOBILE_LINE_RATE * (b_mobile_lines - 1) # 1st line free
            bz_m_price_y2 = BREEZELINE_MOBILE_LINE_RATE * b_mobile_lines
            has_mobile_promo = True
        else:
            bz_m_price_y1 = BREEZELINE_MOBILE_LINE_RATE * b_mobile_lines
            bz_m_price_y2 = BREEZELINE_MOBILE_LINE_RATE * b_mobile_lines
            has_mobile_promo = False

        bz_t_price = BREEZELINE_STREAM_TV_RATE if b_include_tv else 0.0
        
        bz_bundle_y1 = bz_i_price + bz_m_price_y1 + bz_t_price
        bz_bundle_y2 = bz_i_price + bz_m_price_y2 + bz_t_price
        
        m_bundle_save_y1 = total_comp_bundle - bz_bundle_y1
        
        comp_2yr_total = total_comp_bundle * 24
        bz_2yr_total = (bz_bundle_y1 * 12) + (bz_bundle_y2 * 12)
        total_2yr_bundle_save = (comp_2yr_total - bz_2yr_total) + bz_i_plan['gift_card']

        with c2:
            st.subheader("Breezeline Matched Triple-Play Bundle")
            st.info(f"**Internet:** Breezeline {bz_i_plan['name']} ({bz_i_plan['speed']}) @ ${bz_i_price:.2f}/mo ({bz_i_plan['lock']} Price Lock)")
            if b_mobile_lines > 0:
                if has_mobile_promo:
                    st.write(f"• **Mobile:** Line 1 FREE for 12 Months, remaining lines @ ${BREEZELINE_MOBILE_LINE_RATE:.2f}/mo")
                else:
                    st.write(f"• **Mobile:** {b_mobile_lines} Line(s) @ ${BREEZELINE_MOBILE_LINE_RATE:.2f}/mo per line")
            if b_include_tv:
                st.write(f"• **Stream TV:** Everyday Favorites @ ${bz_t_price:.2f}/mo")
            st.write(f"• **Initial Monthly Cost:** **${bz_bundle_y1:.2f}/mo**")
            if bz_i_plan['gift_card'] > 0:
                st.write(f"• **Switching Promo:** ${bz_i_plan['gift_card']} Prepaid Visa Gift Card")

        if m_bundle_save_y1 > 0:
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Monthly Bundle Savings", f"${m_bundle_save_y1:.2f}/mo")
            mc2.metric("2-Year Total Saved Value", f"${total_2yr_bundle_save:.2f}")
            mc3.metric("Breezeline Monthly Total", f"${bz_bundle_y1:.2f}/mo")

            st.markdown(f"""
            <div class="pitch-box">
                <h3 style="margin-top:0; color: #14532d;">🎤 Human Spoken Pitch (Full Bundle):</h3>
                <p class="pitch-text">
                    "Hey, I completely understand how frustrating it is when utility bills keep climbing every year. When you bundle your internet, mobile, and TV together with Breezeline, we guarantee your internet rate for <strong>{bz_i_plan['lock']}</strong>, give you free equipment, and even include a completely free unlimited mobile line for an entire year on our 500 Meg and 1 Gig plans. Your total initial monthly bill drops to just <strong>${bz_bundle_y1:.2f} a month</strong>, saving you <strong>${m_bundle_save_y1:.2f} every month</strong>. Over two years, that puts <strong>${total_2yr_bundle_save:.2f}</strong> back in your pocket plus a switching gift card. Let us handle the setup risk free today."
                </p>
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 2: LOG CUSTOMER INTERACTION ====================
with tab_nav2:
    st.header("Kiosk Lead & Interaction Logger")
    st.write("Enter the customer's details and active account information to record the lead:")

    with st.form("lead_form", clear_on_submit=True):
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            st.subheader("Customer Contact Details")
            lead_name = st.text_input("Customer Name", placeholder="Jane Doe")
            lead_phone = st.text_input("Phone Number", placeholder="555-0199")
            lead_email = st.text_input("Email Address", placeholder="jane.doe@example.com")
            lead_address = st.text_input("Street Address", placeholder="123 Main St, Cumberland MD")
            
        with col_l2:
            st.subheader("Account & Status Info")
            lead_account = st.text_input("Breezeline Account # (If existing customer)", placeholder="123456789")
            lead_pin = st.text_input("Account Security PIN", placeholder="1234", type="password")
            lead_provider = st.selectbox("Current Provider", ["Xfinity", "AT&T", "Verizon", "Satellite", "DSL/None", "Old Breezeline / Atlantic Broadband", "Other"])
            
            lead_status = st.selectbox("Interaction Outcome", [
                "Sales Closed",
                "Follow Up",
                "Interested but address not Serviceable",
                "Billing",
                "Activation",
                "Equipment Return"
            ])
            
        lead_notes = st.text_area("Quick Notes / Objections / Follow-up Details", placeholder="Objection: wants to discuss with spouse first.")
        
        submitted = st.form_submit_button("Log Kiosk Interaction")
        
        if submitted:
            save_lead(
                lead_name or "Anonymous",
                lead_phone or "N/A",
                lead_email or "N/A",
                lead_address or "N/A",
                lead_account or "N/A",
                lead_pin or "N/A",
                lead_provider,
                lead_status,
                lead_notes or "No notes"
            )
            st.success(f"✓ Interaction for '{lead_name or 'Anonymous'}' has been saved securely to your local database!")

# ==================== TAB 3: PERFORMANCE DASHBOARD ====================
with tab_nav3:
    st.header("Cumberland Mall Daily Kiosk Performance")
    
    leads_df = load_leads()
    
    if leads_df.empty:
        st.info("No customer interactions logged yet. Head over to the interaction form tab to add your first daily lead!")
    else:
        total_interactions = len(leads_df)
        
        closed_sales = len(leads_df[leads_df['Status'].str.contains("Sales Closed|Sale Closed", case=False, na=False)])
        follow_ups = len(leads_df[leads_df['Status'].str.contains("Follow Up|Warm Lead", case=False, na=False)])
        unserviceable = len(leads_df[leads_df['Status'].str.contains("not Serviceable", case=False, na=False)])
        billing = len(leads_df[leads_df['Status'].str.contains("Billing", case=False, na=False)])
        activation = len(leads_df[leads_df['Status'].str.contains("Activation", case=False, na=False)])
        equip_return = len(leads_df[leads_df['Status'].str.contains("Equipment Return", case=False, na=False)])
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Kiosk Pitches", total_interactions)
        with k2:
            st.metric("Sales Closed", closed_sales, delta=f"+{closed_sales}")
        with k3:
            st.metric("Follow Ups Scheduled", follow_ups)
        with k4:
            close_rate = (closed_sales / total_interactions) * 100 if total_interactions > 0 else 0
            st.metric("Kiosk Close Rate", f"{close_rate:.1f}%")

        st.markdown("---")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.subheader("Competitor Market Share")
            comp_counts = leads_df['Current Provider'].value_counts()
            st.bar_chart(comp_counts)
            
        with col_d2:
            st.subheader("Outcome Summary")
            outcome_counts = leads_df['Status'].value_counts()
            st.write(outcome_counts)
            
        st.subheader("All Logged Kiosk Interactions")
        st.dataframe(leads_df.sort_index(ascending=False), use_container_width=True)

# Footer Credit
st.markdown("""
<div class="footer-credit">
    ⚡ Breezeline Kiosk Suite | Compiled & Customized for Kiosk Operations by <strong>Darius/banit3</strong> ⚡
</div>
""", unsafe_allow_html=True)
