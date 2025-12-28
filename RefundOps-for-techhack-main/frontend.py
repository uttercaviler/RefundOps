import streamlit as st
import requests
import os
import time

# --- CONFIG ---
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RefundOps Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN CSS STYLING (The "Premium" Look) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary-color: #3b82f6; 
        --success-color: #10b981;
        --danger-color: #ef4444;
        --background-dark: #0f172a;
        --card-bg: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    /* Global Overrides */
    .stApp {
        background-color: var(--background-dark);
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        color: white !important;
    }

    /* Custom Cards / Glassmorphism */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }

    /* Status Indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.025em;
        text-transform: uppercase;
    }
    
    .status-running {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    
    .status-stopped {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Terminal/Logs Window */
    .log-window {
        background-color: #0d1117;
        border-radius: 12px;
        border: 1px solid #30363d;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        padding: 16px;
        height: 400px;
        overflow-y: auto;
        color: #c9d1d9;
        font-size: 13px;
        line-height: 1.5;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .log-line {
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 2px 0;
    }
    .log-timestamp { color: #6e7681; margin-right: 8px; user-select: none; }
    .log-info { color: #58a6ff; }
    .log-error { color: #f85149; }
    .log-success { color: #3fb950; }

    /* Custom Buttons Override */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        border: none;
    }
    
    /* Primary Action Button Style */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(59, 130, 246, 0.4);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Gallery Images */
    .stImage > img {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease;
    }
    .stImage > img:hover {
        transform: scale(1.02);
    }

</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- FUNCTIONS ---
def check_status():
    try:
        res = requests.get(f"{BACKEND_URL}/status")
        if res.status_code == 200:
            return res.json().get("running", False)
    except:
        return False
    return False

def get_logs():
    try:
        res = requests.get(f"{BACKEND_URL}/logs")
        if res.status_code == 200:
            return res.json().get("logs", [])
    except:
        return []
    return []

def login(username, password):
    try:
        res = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            return True, "Login Successful"
        else:
            return False, f"Login Failed: {res.json().get('detail', res.text)}"
    except Exception as e:
        return False, f"Connection Error: {e}"

def signup(username, password, gmail_email, gmail_pass):
    try:
        data = {
            "username": username,
            "password": password,
            "gmail_email": gmail_email,
            "gmail_app_pass": gmail_pass
        }
        res = requests.post(f"{BACKEND_URL}/signup", json=data)
        if res.status_code == 200:
            return True, "Sign Up Successful! Please log in."
        else:
            return False, f"Sign Up Failed: {res.json().get('detail', res.text)}"
    except Exception as e:
        return False, f"Connection Error: {e}"

def start_bot():
    try:
        requests.post(f"{BACKEND_URL}/start")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to start bot: {e}")

def stop_bot():
    try:
        requests.post(f"{BACKEND_URL}/stop")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to stop bot: {e}")

def get_metrics():
    try:
        res = requests.get(f"{BACKEND_URL}/stats")
        if res.status_code == 200:
            return res.json()
    except:
        return {}
    return {}

# --- PAGES ---

if not st.session_state.logged_in:
    # LOGIN PAGE - CENTERED AND MODERN
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True) # Spacer
        
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h1 style="margin-bottom: 0.5rem;">✈️ RefundOps</h1>
            <p style="color: #94a3b8; margin-bottom: 2rem;">Secure Access Portal</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        # --- LOGIN TAB ---
        with tab1:
            with st.form("login_form"):
                st.markdown("### Welcome Back")
                l_username = st.text_input("Username", placeholder="admin")
                l_password = st.text_input("Password", type="password", placeholder="••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚀 Enter Dashboard", type="primary")
                
                if submitted:
                    if l_username and l_password:
                        with st.spinner("Authenticating..."):
                            time.sleep(0.5)
                            success, msg = login(l_username, l_password)
                            if success:
                                st.session_state.logged_in = True
                                st.session_state.user_email = l_username
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        st.warning("Please provide credentials.")

        # --- SIGNUP TAB ---
        with tab2:
            with st.form("signup_form"):
                st.markdown("### Create Account")
                st.info("Your Gmail credentials are required for the bot to check emails.")
                
                s_username = st.text_input("Choose Username", placeholder="e.g. refund_admin")
                s_password = st.text_input("Choose Password", type="password")
                
                st.markdown("#### Bot Connectivity")
                s_gmail = st.text_input("Gmail Address", placeholder="bot@gmail.com")
                s_app_pass = st.text_input("App Password (16 chars)", type="password", placeholder="xxxx xxxx xxxx xxxx")
                
                st.markdown("<br>", unsafe_allow_html=True)
                s_submitted = st.form_submit_button("✨ Create Account", type="primary")
                
                if s_submitted:
                    if s_username and s_password and s_gmail and s_app_pass:
                        with st.spinner("Creating secure account..."):
                            success, msg = signup(s_username, s_password, s_gmail, s_app_pass)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    else:
                        st.warning("All fields are required.")

else:
    # DASHBOARD
    
    # 1. Header Area
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.title("RefundOps Commander")
        st.markdown(f"<p style='color: #94a3b8;'>Welcome back, <span style='color: #3b82f6;'>{st.session_state.user_email}</span></p>", unsafe_allow_html=True)
    with col_head_2:
        st.markdown("<div style='text-align: right; padding-top: 20px;'>", unsafe_allow_html=True)
        if st.button("Logout 🔒", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 1.5. Impact & Complexity Metrics
    stats = get_metrics()
    refund_count = stats.get('refunds_processed', 0)
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 20px; position: relative;">
            <p style="margin:0; color:#94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Refunds Processed</p>
            <h2 style="margin: 5px 0 10px 0; font-size: 2.5rem; font-weight: 700;">{refund_count}</h2>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; margin-top: 8px;">
                <p style="margin:0; font-size: 0.8rem; color: #3b82f6;">⚡ {refund_count * 22:,} <span style="color: #64748b;">Actions Automating</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 20px;">
            <p style="margin:0; color:#94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Time Saved</p>
            <h2 style="margin: 5px 0 10px 0; font-size: 2.5rem; font-weight: 700; color: #3b82f6;">{stats.get('time_saved_minutes', 0)}<span style="font-size: 1rem; color: #64748b;">m</span></h2>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; margin-top: 8px;">
                <p style="margin:0; font-size: 0.8rem; color: #10b981;">⌨️ {refund_count * 48:,} <span style="color: #64748b;">Keystrokes Saved</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 20px;">
            <p style="margin:0; color:#94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Value Recovered</p>
            <h2 style="margin: 5px 0 10px 0; font-size: 2.5rem; font-weight: 700; color: #10b981;">₹{stats.get('money_saved_inr', 0):,}</h2>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; margin-top: 8px;">
                <p style="margin:0; font-size: 0.8rem; color: #94a3b8;">Avg ₹4,500 / claim</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Status & Control Panel
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    status_col_1, status_col_2, status_col_3 = st.columns([2, 5, 2])
    
    is_running = check_status()
    
    with status_col_1:
        st.markdown("### System Status")
        if is_running:
            st.markdown('<div class="status-badge status-running">● SYSTEM ACTIVE</div>', unsafe_allow_html=True)
            st.caption("Listening for emails...")
        else:
            st.markdown('<div class="status-badge status-stopped">● SYSTEM PAUSED</div>', unsafe_allow_html=True)
            st.caption("Waiting for manual start")
            
    with status_col_3:
        st.markdown("### Controls")
        if is_running:
            if st.button("⏹ STOP AGENT", type="secondary", use_container_width=True):
                stop_bot()
        else:
            if st.button("▶ START AGENT", type="primary", use_container_width=True):
                start_bot()
    
    st.markdown('</div>', unsafe_allow_html=True) # End glass card

    # 3. Main Content: Logs & Visuals
    
    main_col_1, main_col_2 = st.columns([1, 1])
    
    with main_col_1:
        st.subheader("📜 Live Terminal Log")
        logs = get_logs()
        
        # Format logs for "terminal" feel
        log_html = ""
        if logs:
            for line in logs:
                # Basic highlighting
                if "ERROR" in line or "Exception" in line:
                    cls = "log-error"
                elif "Found" in line or "Complete" in line or "Success" in line:
                    cls = "log-success"
                elif "Thinking" in line or "Processing" in line:
                    cls = "log-info"
                else:
                    cls = ""
                    
                log_html += f'<div class="log-line"><span class="{cls}">{line}</span></div>'
        else:
            log_html = '<div class="log-line" style="color: #6e7681;">// System initialized. Waiting for output...</div>'
            
        st.markdown(f'<div class="log-window">{log_html}</div>', unsafe_allow_html=True)
        
        if is_running:
            time.sleep(2)
            st.rerun()

    with main_col_2:
        st.subheader("📸 Live Evidence")
        
        # Create a container for the gallery
        gallery_container = st.container()
        
        try:
            res = requests.get(f"{BACKEND_URL}/screenshots")
            if res.status_code == 200:
                images = res.json().get("screenshots", [])
                if images:
                    # Show latest large
                    st.image(images[0], caption="Latest Activity", use_container_width=True)
                    
                    # Show thumbnails needed? Maybe just list recent ones in an expander
                    if len(images) > 1:
                        with st.expander("Recent History"):
                            hist_cols = st.columns(3)
                            for idx, img_path in enumerate(images[1:7]): # Show max 6 more
                                with hist_cols[idx % 3]:
                                    st.image(img_path, caption=img_path, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="height: 400px; border: 2px dashed #30363d; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #6e7681;">
                        <div style="text-align: center;">
                            <span style="font-size: 48px;">📷</span><br>
                            No screenshots captured yet
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Gallery Error: {e}")
