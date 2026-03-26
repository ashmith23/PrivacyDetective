import time
import csv
import os
import json
import sys
import datetime
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:
    from engine.classifier import identify
    from engine.consent_mgr import handle_consent
except ImportError:
    # Fallback for standalone testing
    def identify(domain): return "tracking"
    def handle_consent(driver, action): return True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.nytimes.com"
MONITOR_TIME = 15 

# --- UTILITIES ---
def get_ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def send_progress(p, msg): 
    # Bridge for React/Streamlit progress bars
    print(f"PROGRESS:{p}:{msg.upper()}", flush=True)

def log_event(label, msg): 
    # Formatting for the 'Glass Log' UI component
    timestamp = get_ts()
    formatted_label = label.upper().ljust(10)
    print(f"[{timestamp}] {formatted_label}: {msg}", flush=True)

# --- CORE AUDIT ENGINE ---
def perform_audit(mode):
    """
    Performs network interception and CDP performance monitoring.
    Captures ScriptDuration (CPU time) and Network Size (Bytes).
    """
    offset = 0 if mode == "accept" else 50
    send_progress(offset + 5, f"INITIALIZING {mode.upper()} STATE")
    fname = os.path.join(BASE_DIR, f"temp_audit_{mode}.csv")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new") 
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Enable Chrome DevTools Protocol for hardware metrics
    driver.execute_cdp_cmd('Performance.enable', {})
    
    banner_detected = False
    start_time = time.time()
    seen_domains = set()
    audit_data = []
    total_tracker_bytes = 0

    try:
        log_event("system", f"spawning forensic browser for {mode.upper()} mode")
        driver.get(TARGET_URL)
        
        # Initial wait to allow banner/scripts to trigger
        time.sleep(5)
        
        if mode != "baseline":
            log_event("signal", f"simulating {mode.upper()} interaction...")
            banner_detected = handle_consent(driver, action=mode)
            log_event("signal", "consent interface acknowledged" if banner_detected else "no banner detected")
        
        send_progress(offset + 30, "INTERCEPTING NETWORK & HARDWARE STACK")
        
        host_domain = TARGET_URL.split('/')[2].replace('www.', '')
        end_monitor = time.time() + MONITOR_TIME
        
        while time.time() < end_monitor:
            for req in list(driver.requests):
                if req.response:
                    try:
                        rel_ts = round(req.date.timestamp() - start_time, 2)
                        req_domain = req.url.split('/')[2]
                        
                        if host_domain not in req_domain and req_domain not in seen_domains:
                            category = identify(req_domain)
                            
                            # Measure actual payload size of the tracker
                            res_size = int(req.response.headers.get('Content-Length', 0))
                            total_tracker_bytes += res_size
                            
                            log_event("intel", f"{category.upper()} | {rel_ts}s | {req_domain} ({res_size} bytes)")
                            
                            audit_data.append([req_domain, category, mode, rel_ts, res_size])
                            seen_domains.add(req_domain)
                    except Exception:
                        continue
            
            time.sleep(0.5)
            
        # EXTRACTION: Get Real CPU Metrics via CDP
        metrics = driver.execute_cdp_cmd('Performance.getMetrics', {})
        perf_map = {m['name']: m['value'] for m in metrics['metrics']}
        
        # ScriptDuration = Total seconds CPU spent executing JavaScript
        js_exec_time = perf_map.get('ScriptDuration', 0)
            
        # Write temporary forensics to CSV
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["domain", "category", "mode", "load_time", "size_bytes"])
            writer.writerows(audit_data)

        return {
            "banner_detected": banner_detected,
            "js_exec_s": js_exec_time,
            "total_bytes": total_tracker_bytes,
            "raw_count": len(audit_data)
        }
        
    finally:
        driver.quit()

def generate_summary(accept_meta, reject_meta):
    """
    Synthesizes CSV data and CDP metrics into the final JSON report.
    """
    send_progress(95, "SYNTHESIZING FORENSIC INTELLIGENCE")
    
    def load_audit_csv(mode):
        path = os.path.join(BASE_DIR, f"temp_audit_{mode}.csv")
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    accept_list = load_audit_csv("accept")
    reject_list = load_audit_csv("reject") if accept_meta['banner_detected'] else []

    # 1. TEMPORAL TELEMETRY
    timeline_map = {}
    for entry in accept_list:
        try:
            sec_bucket = int(float(entry['load_time']))
            timeline_map[sec_bucket] = timeline_map.get(sec_bucket, 0) + 1
        except: continue
        
    formatted_timeline = [{"time": f"{k}s", "requests": v} for k, v in sorted(timeline_map.items())]

    # 2. RESOURCE DRAIN & PERFORMANCE TAX
    # Performance Tax = % of total monitor time spent running scripts
    js_time = accept_meta.get('js_exec_s', 0)
    perf_tax = min(100, round((js_time / MONITOR_TIME) * 100, 1))
    
    # Carbon calculation: ~0.8g CO2 per MB transferred
    mb_total = accept_meta.get('total_bytes', 0) / (1024 * 1024)
    carbon_g = round(mb_total * 0.8, 4)

    # 3. COMPLIANCE SCORING
    banner_status = accept_meta['banner_detected']
    if not banner_status:
        final_score = "0%"
    else:
        leaks = [t for t in reject_list if t['category'].lower() != "functional"]
        if not accept_list:
            final_score = "100%"
        else:
            score_calc = max(0, 100 - int((len(leaks) / len(accept_list) * 100)))
            final_score = f"{score_calc}%"

    # 4. FINAL EXPORT
    report_data = {
        "score": final_score, 
        "banner_found": banner_status, 
        "accept_total_trackers": accept_list, 
        "reject_total_trackers": reject_list,
        "timeline_data": formatted_timeline,
        "performance_metrics": {
            "execution_time_s": round(js_time, 2),
            "performance_tax_percent": perf_tax,
            "data_transfer_mb": round(mb_total, 2),
            "carbon_footprint_g": carbon_g,
            "battery_drain_score": "high" if perf_tax > 35 else "medium" if perf_tax > 12 else "low"
        }
    }

    report_path = os.path.join(BASE_DIR, 'reports', "latest_audit.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4)
    
    log_event("system", "forensic summary written to storage")
    send_progress(100, "AUDIT COMPLETE")

if __name__ == "__main__":
    # Sequential forensic execution
    accept_metadata = perform_audit("accept")
    
    reject_metadata = None
    if accept_metadata['banner_detected']:
        reject_metadata = perform_audit("reject")
        
    generate_summary(accept_metadata, reject_metadata)
