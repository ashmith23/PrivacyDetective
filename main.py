import time
import csv
import os
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from engine.classifier import identify
from engine.consent_mgr import handle_consent

# CONFIG AREA
TARGET_URL = "https://www.nytimes.com" # test site link
MONITOR_TIME = 20  # seconds to watch traffic per session

def get_new_driver():
    """Creates a fresh, clean-slate browser instance"""
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    #options.add_argument("--headless") # for running w/o popup.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def perform_audit(mode_to_test):
    """Handles a full lifecycle: Open -> Interact -> Monitor -> Save -> Close"""
    print(f"\n--- 🕵️ INITIATING SESSION: {mode_to_test.upper()} MODE ---")
    driver = get_new_driver()
    
    banner_found = False
    effective_mode = mode_to_test

    try:
        driver.get(TARGET_URL)
        time.sleep(12) # wait for site to load.

        # 1. interaction logic.
        if mode_to_test != "baseline":
            banner_found = handle_consent(driver, action=mode_to_test)
        
        # fallback if no banner appears.
        if mode_to_test != "baseline" and not banner_found:
            print("ℹ️ No consent banner found. Categorizing as 'BASELINE'.")
            effective_mode = "baseline"

        # 2. traffic capture.
        print(f"📡 Monitoring {effective_mode} traffic for {MONITOR_TIME}s...")
        time.sleep(MONITOR_TIME)

        # 3. data processing.
        captured_data = []
        seen_domains = set()
        base_domain = TARGET_URL.split('/')[2].replace('www.', '')

        for req in driver.requests:
            if req.response:
                domain = req.url.split('/')[2]
                if base_domain not in domain and domain not in seen_domains:
                    category = identify(domain)
                    captured_data.append([domain, category, effective_mode])
                    seen_domains.add(domain)

        # 4. saving to csv file.
        fname = f"audit_{effective_mode}.csv"
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Domain", "Category", "Mode"])
            writer.writerows(captured_data)
        
        print(f"✅ Success: {len(captured_data)} domains saved to {fname}")

    finally:
        driver.quit() #reset, wipe session and cookies.
    
    return banner_found

def generate_summary():
    """Final analysis comparing Accept and Reject states"""
    acc_file = "audit_accept.csv"
    rej_file = "audit_reject.csv"

    if not os.path.exists(acc_file) or not os.path.exists(rej_file):
        print("\n📊 SUMMARY: Comparison unavailable (Missing audit files).")
        return

    def get_data(fname):
        with open(fname, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            return {row[0]: row[1] for row in reader}

    acc_data = get_data(acc_file)
    rej_data = get_data(rej_file)

    acc_set = set(acc_data.keys())
    rej_set = set(rej_data.keys())

    # analysis sets
    honest_trackers = acc_set - rej_set
    persistent_trackers = rej_set.intersection(acc_set)
    spite_trackers = rej_set - acc_set

    print(f"\n{'='*65}")
    print(f"📊 PRIVACY AUDIT SUMMARY: {TARGET_URL}")
    print(f"{'='*65}")
    print(f"✅ Honest Trackers (Blocked by Reject):  {len(honest_trackers)}")
    print(f"⚠️  Persistent Trackers (Ignored Reject): {len(persistent_trackers)}")
    print(f"🧩 Spite Trackers (Only in Reject flow): {len(spite_trackers)}")
    
    if spite_trackers:
        print(f"\n💡 NOTE: {len(spite_trackers)} domains were unique to the REJECT flow.")
        print("   These are likely Consent Management Scripts (Overhead).")

    if honest_trackers:
        print(f"\n🔍 TRACKERS THAT RESPECTED YOUR CHOICE:")
        for d in sorted(honest_trackers):
            print(f"  - {d}")

    # calculate privacy grade
    total_potential = len(acc_set.union(rej_set))
    if total_potential > 0:
        # compliance is essentially (honest / total)
        score = (len(honest_trackers) / len(acc_set)) * 100 if len(acc_set) > 0 else 0
        print(f"\n⚖️  SITE PRIVACY GRADE: {score:.1f}% Compliance")
    print(f"{'='*65}\n")

def run_full_suite():
    print(f"🚀 BOOTING AUDIT SUITE (Order: ACCEPT -> REJECT)")
    
    # PASS 1: ACCEPT
    banner_exists = perform_audit("accept")

    # PASS 2: REJECT (only if a banner exists)
    if banner_exists:
        print("\n🔄 Restarting for Pass 2 (Testing Privacy Rejection)...")
        perform_audit("reject")
        
        # FINAL: Report
        generate_summary()
    else:
        print("\n⏭️ No banner found. Single baseline audit complete.")

if __name__ == "__main__":
    run_full_suite()