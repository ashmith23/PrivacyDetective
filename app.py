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
REPORT_DIR = os.path.join(BASE_DIR, "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "latest_audit.json")

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# --- 2. SESSION STATE ---
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = None
if 'audit_complete' not in st.session_state:
    st.session_state.audit_complete = False
if 'target_url' not in st.session_state:
    st.session_state.target_url = ""

# --- 3. CONSTANTS & BRANDING ---
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
    "pubmatic": "PubMatic", "rubiconproject": "Magnite", "openx": "OpenX",
    "taboola": "Taboola", "outbrain": "Outbrain", "criteo": "Criteo",
    "scorecardresearch": "Comscore", "ttads": "TikTok (ByteDance)",
    "twitter": "X (Twitter)", "t.co": "X (Twitter)",
    "hotjar": "Hotjar", "crwdcntrl": "Adobe", "omtrdc": "Adobe", "demdex": "Adobe"
}

# --- 4. CORE LOGIC FUNCTIONS ---
def get_entity_refined(domain):
    """Identifies parent company or uses heuristics for unknown domains (Forbes fix)."""
    for key, owner in ENTITY_LOOKUP.items():
        if key in domain.lower(): return owner
    
    # Heuristic Fallback
    d_lower = domain.lower()
    if any(x in d_lower for x in ["pixel", "track", "collect", "measure", "telemetry"]):
        return "Independent (Ad-Tracking)"
    if any(x in d_lower for x in ["ad-", "ads.", "bid", "yield", "mktg"]):
        return "Independent (Marketing)"
    if any(x in d_lower for x in ["cdn", "static", "assets", "js."]):
        return "Independent (Infrastructure)"
    return "Independent / Other"

def clear_search_only():
    st.session_state.target_url = ""

def generate_pdf_report(dataframe, url, score, compliant_list, violation_list, graph_images=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", 'B', 24); pdf.set_text_color(29, 29, 31)
    pdf.cell(0, 20, "Privacy Detective: Forensic Report", ln=True)
    pdf.set_font("Helvetica", '', 12); pdf.set_text_color(134, 134, 139)
    pdf.cell(0, 10, f"Target URL: {str(url)}", ln=True)
    pdf.cell(0, 10, f"Audit Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    
    # Score Box
    pdf.ln(10)
    pdf.set_fill_color(245, 245, 247); pdf.rect(10, 55, 190, 25, 'F')
    pdf.set_xy(15, 60); pdf.set_font("Helvetica", 'B', 16); pdf.set_text_color(0, 113, 227)
    pdf.cell(0, 10, f"Privacy Compliance Score: {str(score)}"); pdf.ln(30)

    # Visualization Section
    if graph_images:
        pdf.set_font("Helvetica", 'B', 14); pdf.set_text_color(29, 29, 31)
        pdf.cell(0, 10, "Forensic Visualizations", ln=True); pdf.ln(5)
        for i, img_buf in enumerate(graph_images):
            if pdf.get_y() > 180: pdf.add_page()
            temp_path = f"temp_graph_{i}.png"
            with open(temp_path, "wb") as f: f.write(img_buf.getbuffer())
            pdf.image(temp_path, x=15, w=180); pdf.ln(10)
            if os.path.exists(temp_path): os.remove(temp_path)

    # Detailed Tracker Inventory
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14); pdf.cell(0, 10, "Full Tracker Inventory", ln=True); pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", 'B', 10); pdf.set_text_color(255, 255, 255); pdf.set_fill_color(29, 29, 31)
    pdf.cell(80, 10, " Domain", fill=True); pdf.cell(60, 10, " Entity", fill=True); pdf.cell(50, 10, " Status", fill=True); pdf.ln()
    
    # Table Rows
    pdf.set_font("Helvetica", '', 9); pdf.set_text_color(29, 29, 31)
    for i, row in dataframe.iterrows():
        bg = (250, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        
        status = "VIOLATION" if str(row['domain']) in violation_list else "COMPLIANT"
        if status == "VIOLATION": pdf.set_text_color(255, 59, 48)
        else: pdf.set_text_color(29, 29, 31)
        
        pdf.cell(80, 9, f" {str(row['domain'])}", fill=True, border='B')
        pdf.cell(60, 9, f" {str(row['Entity'])}", fill=True, border='B')
        pdf.cell(50, 9, f" {status}", fill=True, border='B')
        pdf.ln()
        if pdf.get_y() > 270: pdf.add_page()

    return pdf.output()

# --- 5. PREMIUM CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: #F5F5F7; }}
    .hero-title {{ font-size: 4rem; font-weight: 800; text-align: center; color: #1d1d1f; letter-spacing: -0.1rem; margin-top: 2rem; background: linear-gradient(180deg, #1d1d1f 0%, #434344 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero-subtitle {{ font-size: 1.2rem; text-align: center; color: #86868b; margin-bottom: 3.5rem; }}
    div[data-testid="stTextInput"] > div > div > input {{ text-align: center; font-size: 1.1rem; padding: 15px; border-radius: 20px; border: 1px solid #D2D2D7; background: white; }}
    .glass-log {{ background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(30px) saturate(200%); border-radius: 30px; padding: 20px; height: 280px; border: 1px solid rgba(255, 255, 255, 0.5); box-shadow: 0 25px 50px rgba(0,0,0,0.08); font-family: 'SF Mono', monospace; overflow: hidden; }}
    .log-entry {{ margin-bottom: 8px; border-left: 3px solid #E5E5E7; padding-left: 15px; font-size: 0.85rem; }}
    .log-system {{ color: {APPLE_BLUE}; font-weight: 600; border-left-color: {APPLE_BLUE}; }}
    .log-detect {{ color: {APPLE_RED}; font-weight: 600; border-left-color: {APPLE_RED}; background: rgba(255, 59, 48, 0.08); padding: 4px 12px; border-radius: 8px; }}
    .footer-box {{ margin-top: 80px; padding: 40px; border-top: 1px solid #D2D2D7; text-align: center; color: #86868b; line-height: 1.6; background: #fbfbfd; }}
    .footer-title {{ color: #1d1d1f; font-weight: 600; font-size: 1.1rem; margin-bottom: 10px; }}
    .footer-text {{ font-size: 0.95rem; max-width: 800px; margin: 0 auto; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("### SYSTEM OVERVIEW")
    st.caption("Forensic Architecture: Headless Chromium engine.")
    st.divider()
    st.markdown("### AUDIT SCOPE")
    st.markdown("- Multi-state Consent Simulation\n- Corporate Hierarchy Mapping\n- Temporal Analysis")

# --- 7. AUDIT INTERFACE ---
st.markdown('<h1 class="hero-title">Privacy Detective</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Exposing hidden trackers and corporate data-sharing networks.</p>', unsafe_allow_html=True)

_, col_center, _ = st.columns([1, 4, 1])
with col_center:
    col_input, col_clear = st.columns([9, 1])
    user_link = col_input.text_input("URL", key="target_url", placeholder="Enter site URL to investigate...", label_visibility="collapsed")
    with col_clear:
        st.button("✕", on_click=clear_search_only, help="Clear text")

_, col_run, _ = st.columns([2, 2, 2])
if col_run.button("Start Forensic Investigation", use_container_width=True) and user_link:
    if os.path.exists(REPORT_FILE): os.remove(REPORT_FILE)
    st.session_state.audit_complete = False
    st.session_state.audit_data = None
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
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, 'r') as f:
            st.session_state.audit_data = json.load(f)
        st.session_state.audit_complete = True
    st.rerun()

# --- 8. DASHBOARD ---
if st.session_state.audit_complete and st.session_state.audit_data:
    data = st.session_state.audit_data
    acc_df = pd.DataFrame(data.get('accept_total_trackers', []))
    rej_df = pd.DataFrame(data.get('reject_total_trackers', []))
    banner_found = data.get('banner_found', False)
    display_score = data.get('score', '0%') if banner_found else "VOID"
    
    if not acc_df.empty:
        acc_df['Entity'] = acc_df['domain'].apply(get_entity_refined)
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Compliance", display_score)
        m2.metric("Trackers", len(acc_df))
        m3.metric("Entities", len(acc_df['Entity'].unique()))
        m4.metric("Dominance", f"{(acc_df['Entity'].value_counts().max() / len(acc_df) * 100 if len(acc_df)>0 else 0):.0f}%")

        t1, t2, t3, t4, t5 = st.tabs(["Forensic Mapping", "Timeline", "Compliance", "Inventory", "Export"])
        
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

        # --- FIX: Safe column access to prevent KeyError ---
        acc_set = set(acc_df['domain']) if 'domain' in acc_df.columns else set()
        rej_set = set(rej_df['domain']) if not rej_df.empty and 'domain' in rej_df.columns else set()
        
        respectful = list(acc_set - rej_set)
        violations = list(rej_set)

        with t3:
            st.write("### Forensic Compliance Check")
            if not banner_found: st.info("No consent banner detected.")
            else:
                col_r, col_n = st.columns(2)
                with col_r:
                    st.write(f"#### Lawful ({len(respectful)})")
                    if respectful: st.dataframe(acc_df[acc_df['domain'].isin(respectful)][['domain', 'category']], use_container_width=True, hide_index=True)
                with col_n:
                    st.write(f"#### Violation Flags ({len(violations)})")
                    if violations: st.dataframe(rej_df[rej_df['domain'].isin(violations)][['domain', 'category']], use_container_width=True, hide_index=True)

        with t4:
            st.write("### Raw Intelligence Inventory")
            c1, c2, c3 = st.columns([2, 1, 1])
            search_query = c1.text_input("Search Domain", placeholder="e.g. doubleclick", label_visibility="collapsed")
            selected_entities = c2.multiselect("Entity", options=sorted(acc_df['Entity'].unique()))
            selected_categories = c3.multiselect("Type", options=sorted(acc_df['category'].unique()))
            filtered_df = acc_df.copy()
            if search_query: filtered_df = filtered_df[filtered_df['domain'].str.contains(search_query, case=False)]
            if selected_entities: filtered_df = filtered_df[filtered_df['Entity'].isin(selected_entities)]
            if selected_categories: filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
            st.dataframe(filtered_df[['domain', 'Entity', 'category']], use_container_width=True, hide_index=True)

        with t5:
            st.write("### Forensic Data Export")
            col_pdf, col_csv = st.columns(2)
            with col_pdf:
                if st.button("Generate Case Report (PDF)", use_container_width=True):
                    with st.spinner("Capturing forensic evidence..."):
                        img_bufs = []
                        for fig in [fig_tree, fig_pie, fig_scatter]:
                            buf = io.BytesIO()
                            fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
                            fig.write_image(buf, format="png", engine="kaleido", width=1200, height=800)
                            img_bufs.append(buf)
                        pdf_out = generate_pdf_report(acc_df, user_link, display_score, respectful, violations, graph_images=img_bufs)
                        st.download_button(label="Download Full PDF", data=bytes(pdf_out), file_name=f"Audit_{datetime.date.today()}.pdf", mime="application/pdf", use_container_width=True)
            with col_csv:
                csv_data = acc_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Export Tracker List (CSV)", data=csv_data, file_name=f"Trackers_{datetime.date.today()}.csv", mime="text/csv", use_container_width=True)

# --- 9. FOOTER ---
st.markdown("""<div class="footer-box"><div class="footer-title">How Privacy Detective Works</div><div class="footer-text">Our engine compares two browser states (Accepted vs. Rejected) to find trackers that ignore user choice. We map these to parent companies to expose the hidden data monopoly.</div><br><div style="font-size: 0.8rem; opacity: 0.6;">Forensic Suite v2.4.0 • Saintgits IMCA Project</div></div>""", unsafe_allow_html=True)