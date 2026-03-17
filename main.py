import time, csv, os, json, sys, datetime
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from engine.classifier import identify
from engine.consent_mgr import handle_consent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.nytimes.com"
MONITOR_TIME = 15 

# --- APPLE-CORE LOGGING UTILITIES ---
def get_ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def send_progress(p, msg): 
    # Maintains the bridge to Streamlit's progress bar
    print(f"PROGRESS:{p}:{msg.upper()}", flush=True)

def log_event(label, msg): 
    # vertical alignment (ljust) ensures a clean column-look in the glass log
    timestamp = get_ts()
    formatted_label = label.upper().ljust(10)
    print(f"[{timestamp}] {formatted_label}: {msg}", flush=True)

# --- CORE AUDIT ENGINE ---
def perform_audit(mode):
    offset = 0 if mode == "accept" else 50
    send_progress(offset + 5, f"INITIALIZING {mode.upper()} STATE")
    fname = os.path.join(BASE_DIR, f"temp_audit_{mode}.csv")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new") 
    options.add_argument("--lang=en-US")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    banner = False
    try:
        log_event("target", f"Analyzing {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(8)
        
        if mode != "baseline":
            log_event("signal", f"Simulating {mode.upper()} interaction...")
            banner = handle_consent(driver, action=mode)
            log_event("signal", "Consent interface acknowledged" if banner else "No banner detected")
        
        send_progress(offset + 30, "INTERCEPTING NETWORK STACK")
        seen = set(); data = []
        host = TARGET_URL.split('/')[2].replace('www.', '')
        
        end = time.time() + MONITOR_TIME
        while time.time() < end:
            for req in list(driver.requests):
                try:
                    dom = req.url.split('/')[2]
                    if host not in dom and dom not in seen:
                        cat = identify(dom)
                        # The "INTEL" label triggers the red highlighting in app.py
                        log_event("intel", f"{cat.upper()} detected via {dom}")
                        data.append([dom, cat, mode])
                        seen.add(dom)
                except: continue
            time.sleep(1)
            
        with open(fname, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows([["domain","category","mode"]] + data)
    finally:
        driver.quit()
    return banner

def generate_summary(banner):
    send_progress(95, "SYNTHESIZING FORENSIC INTELLIGENCE")
    def get_csv(mode):
        p = os.path.join(BASE_DIR, f"temp_audit_{mode}.csv")
        if not os.path.exists(p): return []
        with open(p, 'r') as f:
            r = csv.reader(f); next(r)
            # load_time creates the data for the Forensic Timeline Heatmap
            return [{"domain": row[0], "category": row[1], "load_time": i * 0.15} for i, row in enumerate(r)]

    acc = get_csv("accept")
    rej = get_csv("reject") if banner else []
    leaks = [i for i in rej if i['category'] != "Functional"]
    
    score_val = f"{max(0, 100 - int((len(leaks)/len(acc)*100)))}%" if (acc and banner) else "VOID"
    
    with open(os.path.join(BASE_DIR, 'reports', "latest_audit.json"), 'w') as f:
        json.dump({
            "score": score_val, 
            "banner_found": banner, 
            "accept_total_trackers": acc, 
            "reject_total_trackers": rej
        }, f)
    
    log_event("system", "Forensic summary written to storage")
    send_progress(100, "AUDIT COMPLETE")

if __name__ == "__main__":
    found = perform_audit("accept")
    if found: perform_audit("reject")
    generate_summary(found)