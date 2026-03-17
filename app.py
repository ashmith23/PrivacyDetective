import streamlit as st
import json, os, subprocess, sys, time, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Privacy Detective", layout="wide", page_icon="🛡️")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(BASE_DIR, "reports", "latest_audit.json")

# --- 2. CONSTANTS & BRANDING ---
APPLE_BLUE = "#0071E3"
APPLE_RED = "#FF3B30"
APPLE_DARK = "#1D1D1F"
CHART_COLORS = ["#5E5CE6", "#BF5AF2", "#FF2D55", "#007AFF", "#AF52DE", "#5856D6"]

ENTITY_LOOKUP = {
    "google": "Alphabet (Google)", "doubleclick": "Alphabet (Google)", "gstatic": "Alphabet (Google)",
    "facebook": "Meta", "fbcdn": "Meta", "instagram": "Meta",
    "amazon": "Amazon", "amzn": "Amazon",
    "microsoft": "Microsoft", "bing": "Microsoft", "clarity": "Microsoft",
    "adnxs": "Microsoft (Xandr)", "adsrvr": "The Trade Desk",
    "scorecardresearch": "Comscore", "ttads": "TikTok (ByteDance)",
    "twitter": "X (Twitter)", "t.co": "X (Twitter)",
    "hotjar": "Hotjar", "crwdcntrl": "Adobe", "omtrdc": "Adobe"
}

# --- 3. CORE LOGIC FUNCTIONS ---
def get_entity(domain):
    for key, owner in ENTITY_LOOKUP.items():
        if key in domain.lower(): return owner
    return "Independent / Other"

def clear_url():
    st.session_state.target_url = ""

def generate_pdf_report(dataframe, url, score, graph_images=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", 'B', 24)
    pdf.set_text_color(29, 29, 31)
    pdf.cell(0, 20, "Privacy Detective: Forensic Report", ln=True)
    
    pdf.set_font("Helvetica", '', 12)
    pdf.set_text_color(134, 134, 139)
    pdf.cell(0, 10, f"Forensic Audit for: {str(url)}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)
    
    # Score Box
    pdf.set_fill_color(245, 245, 247)
    pdf.rect(10, 55, 190, 25, 'F')
    pdf.set_xy(15, 60)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(0, 113, 227)
    pdf.cell(0, 10, f"Compliance Score: {str(score)}")
    pdf.ln(30)

    # Embed Graphs
    if graph_images:
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_text_color(29, 29, 31)
        pdf.cell(0, 10, "Forensic Visualizations", ln=True)
        pdf.ln(5)
        for i, img_buf in enumerate(graph_images):
            if pdf.get_y() > 180: pdf.add_page()
            temp_path = f"temp_graph_{i}.png"
            with open(temp_path, "wb") as f:
                f.write(img_buf.getbuffer())
            pdf.image(temp_path, x=15, w=180)
            pdf.ln(10)
            if os.path.exists(temp_path): os.remove(temp_path)
        pdf.add_page()

    # Data Table
    pdf.set_font("Helvetica", 'B', 10); pdf.set_text_color(255, 255, 255); pdf.set_fill_color(29, 29, 31)
    pdf.cell(85, 10, " Domain", fill=True); pdf.cell(60, 10, " Entity", fill=True); pdf.cell(45, 10, " Category", fill=True); pdf.ln()
    
    pdf.set_font("Helvetica", '', 9); pdf.set_text_color(29, 29, 31)
    for i, row in dataframe.reset_index().iterrows():
        bg = (250, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.cell(85, 9, f" {str(row['domain'])}", fill=True, border='B')
        pdf.cell(60, 9, f" {str(row['Entity'])}", fill=True, border='B')
        if row['category'] != "Functional": pdf.set_text_color(255, 59, 48)
        pdf.cell(45, 9, f" {str(row['category'])}", fill=True, border='B')
        pdf.set_text_color(29, 29, 31); pdf.ln()
        if pdf.get_y() > 270: pdf.add_page()
            
    return pdf.output()

# --- 4. PREMIUM CSS (Centered Input Hierarchy) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: #F5F5F7; }}
    
    .hero-title {{ 
        font-size: 4rem; font-weight: 800; text-align: center; color: #1d1d1f; 
        letter-spacing: -0.1rem; margin-top: 2rem;
        background: linear-gradient(180deg, #1d1d1f 0%, #434344 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{ font-size: 1.2rem; text-align: center; color: #86868b; margin-bottom: 3.5rem; }}
    
    /* Center the Input Process */
    div[data-testid="stTextInput"] > div > div > input {{
        text-align: center;
        font-size: 1.1rem;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #D2D2D7;
        background: white;
    }}

    .status-bar {{
        background: rgba(0, 113, 227, 0.05); border: 1px solid rgba(0, 113, 227, 0.1);
        border-radius: 12px; padding: 10px 20px; margin-bottom: 25px;
        display: flex; justify-content: space-around;
    }}
    .status-item {{ font-family: 'SF Mono', monospace; font-size: 0.75rem; color: {APPLE_BLUE}; }}
    .status-label {{ color: #86868b; font-weight: 400; margin-right: 8px; font-size: 0.7rem; }}

    .glass-log {{
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(30px) saturate(200%);
        border-radius: 30px; padding: 20px; height: 280px; 
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 25px 50px rgba(0,0,0,0.08);
        font-family: 'SF Mono', monospace; font-size: 0.85rem; color: {APPLE_DARK};
        overflow: hidden; margin-top: 10px;
    }}
    
    .log-entry {{ margin-bottom: 8px; border-left: 3px solid #E5E5E7; padding-left: 15px; }}
    .log-system {{ color: {APPLE_BLUE}; font-weight: 600; border-left-color: {APPLE_BLUE}; }}
    .log-detect {{ color: {APPLE_RED}; font-weight: 600; border-left-color: {APPLE_RED}; background: rgba(255, 59, 48, 0.08); padding: 4px 12px; border-radius: 8px; }}
    
    div[data-testid="stMetric"] {{
        background: white !important; border-radius: 28px !important; 
        border: 1px solid #E5E5E7 !important; padding: 20px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### SYSTEM OVERVIEW")
    st.caption("Forensic Architecture: Headless Chromium engine.")
    st.divider()
    st.markdown("### AUDIT SCOPE")
    st.markdown("- Multi-state Consent Simulation\n- Corporate Hierarchy Mapping\n- Temporal Analysis")

# --- 6. AUDIT INTERFACE ---
st.markdown('<h1 class="hero-title">Privacy Detective</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Exposing hidden trackers and corporate data-sharing networks.</p>', unsafe_allow_html=True)

if 'target_url' not in st.session_state: st.session_state.target_url = ""

# Centering the input layout
_, col_center, _ = st.columns([1, 4, 1])
with col_center:
    col_input, col_clear = st.columns([9, 1])
    user_link = col_input.text_input("URL", key="target_url", placeholder="Enter site URL to investigate...", label_visibility="collapsed")
    with col_clear:
        st.button("✕", on_click=clear_url)

_, col_run, _ = st.columns([2, 2, 2])
if col_run.button("Start Forensic Investigation", use_container_width=True) and user_link:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        p_bar = st.progress(0); s_text = st.empty(); l_area = st.empty()
    
    live_logs = ['<div class="log-entry log-system">SYSTEM: Deploying investigative engine...</div>']
    process = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "main.py"), user_link],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None: break
        if line.startswith("PROGRESS:"):
            parts = line.split(":")
            p_bar.progress(int(parts[1])); s_text.markdown(f"**Status:** `{parts[2].strip()}`")
        elif line.strip():
            msg = line.strip()
            fmt = "log-detect" if "INTEL:" in msg else "log-system" if any(x in msg for x in ["SYSTEM:", "SIGNAL:", "TARGET:"]) else ""
            live_logs.append(f'<div class="log-entry {fmt}">{msg}</div>')
            l_area.markdown(f'<div class="glass-log">{"".join(live_logs[-8:])}</div>', unsafe_allow_html=True)
    st.rerun()

# --- 7. DASHBOARD ---
if os.path.exists(REPORT_FILE):
    with open(REPORT_FILE, 'r') as f: data = json.load(f)
    acc_df = pd.DataFrame(data.get('accept_total_trackers', []))
    rej_df = pd.DataFrame(data.get('reject_total_trackers', []))
    banner_found = data.get('banner_found', False)
    display_score = data.get('score', '0%') if banner_found else "VOID"
    
    if not acc_df.empty:
        acc_df['Entity'] = acc_df['domain'].apply(get_entity)
        st.divider()
        
        st.markdown(f"""<div class="status-bar">
            <div class="status-item"><span class="status-label">CASE-ID</span>{datetime.datetime.now().strftime('%y%m%d')}</div>
            <div class="status-item"><span class="status-label">ENGINE</span>CHROMIUM</div>
            <div class="status-item"><span class="status-label">LOCALE</span>EN-US</div>
        </div>""", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Compliance", display_score)
        m2.metric("Trackers", len(acc_df))
        m3.metric("Entities", len(acc_df['Entity'].unique()))
        m4.metric("Dominance", f"{(acc_df['Entity'].value_counts().max() / len(acc_df) * 100):.0f}%")

        t1, t2, t3, t4, t5 = st.tabs(["Forensic Mapping", "Temporal Analysis", "Compliance", "Intelligence", "Export"])
        
        with t1:
            c1, c2 = st.columns(2)
            fig_tree = px.treemap(acc_df, path=[px.Constant("Trackers"), 'Entity', 'category'], color='Entity', color_discrete_sequence=CHART_COLORS)
            c1.write("#### Corporate Treemap")
            c1.plotly_chart(fig_tree, use_container_width=True)
            
            fig_pie = px.pie(acc_df, names='category', hole=0.6, color_discrete_sequence=CHART_COLORS)
            c2.write("#### Category Distribution")
            c2.plotly_chart(fig_pie, use_container_width=True)

        with t2:
            st.write("### Sequence of Execution")
            timeline_df = acc_df.copy()
            if 'load_time' not in timeline_df.columns: timeline_df['load_time'] = timeline_df.index * 0.12 
            fig_scatter = px.scatter(timeline_df, x='load_time', y='Entity', color='category', color_discrete_sequence=CHART_COLORS, height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)

        with t3:
            st.write("### Forensic Compliance Check")
            if not banner_found: st.info("No consent banner detected.")
            else:
                acc_set, rej_set = set(acc_df['domain']), set(rej_df['domain'])
                respectful, non_compliant = acc_set - rej_set, rej_set
                col_r, col_n = st.columns(2)
                with col_r:
                    st.write(f"#### Lawful ({len(respectful)})")
                    if respectful: st.dataframe(acc_df[acc_df['domain'].isin(respectful)][['domain', 'category']], use_container_width=True, hide_index=True)
                with col_n:
                    st.write(f"#### Violation Flags ({len(non_compliant)})")
                    if non_compliant: st.dataframe(rej_df[rej_df['domain'].isin(non_compliant)][['domain', 'category']], use_container_width=True, hide_index=True)

        with t4:
            st.write("### Raw Intelligence Inventory")
            st.dataframe(acc_df[['domain', 'Entity', 'category']], use_container_width=True, hide_index=True)

        with t5:
            st.write("### Forensic Data Export")
            if st.button("Generate Case Report (PDF with All Visuals)"):
                with st.spinner("Capturing forensic evidence..."):
                    img_bufs = []
                    for fig in [fig_tree, fig_pie, fig_scatter]:
                        buf = io.BytesIO()
                        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
                        fig.write_image(buf, format="png", engine="kaleido", width=1200, height=800)
                        img_bufs.append(buf)
                    
                    pdf_out = generate_pdf_report(acc_df, user_link, display_score, graph_images=img_bufs)
                    st.download_button(label="Download Full Forensic PDF", data=bytes(pdf_out), file_name="Privacy_Detective_Report.pdf", mime="application/pdf", use_container_width=True)

            st.download_button(label="Export Raw Evidence (CSV)", data=acc_df.to_csv(index=False).encode('utf-8'), file_name="Evidence_Data.csv", mime="text/csv", use_container_width=True)