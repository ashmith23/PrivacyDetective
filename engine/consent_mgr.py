from selenium.webdriver.common.by import By
import time

def handle_consent(driver, action="reject"):
    """
    Handles cookie consent banners with a weighted priority approach.
    Now handles NYTimes-style anomalies where 'Reject All' exists alongside 'Save'.
    """
    print(f" [CONSENT] Starting deep-scan for {action.upper()}...")
    
    # PHASE 1 Keywords
    primary_keywords = ["reject", "decline", "necessary", "refuse", "manage"] if action == "reject" \
                       else ["accept", "agree", "allow", "okay"]
    
    # PHASE 2 Priorities (Tiered for Dark Patterns)
    # Level 1: Hard Rejection (Highest Priority)
    prio_1 = ["reject all", "reject everything", "disagree"]
    # Level 2: Technical Confirmation
    prio_2 = ["save", "confirm", "submit", "apply", "keep"]
    # Level 3: Generic exits
    prio_3 = ["exit", "choices", "close"]

    def attempt_js_click(priority_groups):
        """
        Modified to accept a list of keyword groups. 
        It scans all groups in order across the DOM and Iframes.
        """
        js_script = """
        function findAndClick(root, priorityGroups) {
            let tags = ['button', 'a', 'div[role="button"]', 'span', 'p'];
            let elems = root.querySelectorAll(tags.join(','));
            
            // Iterate through priority levels (Prio 1 first, then Prio 2...)
            for (let words of priorityGroups) {
                for (let el of elems) {
                    let text = el.innerText ? el.innerText.toLowerCase().trim() : "";
                    
                    if (words.some(word => text === word || (text.includes(word) && text.length < 25))) {
                        if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                            el.style.border = "5px solid red";
                            el.style.backgroundColor = "yellow";
                            el.click();
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        // 1. Search Main Document
        let found = findAndClick(document, arguments[0]);
        
        // 2. Search Iframes
        if (!found) {
            let iframes = document.querySelectorAll('iframe');
            for (let i = 0; i < iframes.length; i++) {
                try {
                    let frameDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    found = findAndClick(frameDoc, arguments[0]);
                    if (found) break;
                } catch (e) {}
            }
        }
        return found;
        """
        # Pass the nested list of priorities to JS
        return driver.execute_script(js_script, priority_groups)

    # --- EXECUTION FLOW ---

    # PHASE 1: INITIAL CLICK
    # We pass primary_keywords as a single-item list to maintain the new JS format
    first_hit = attempt_js_click([primary_keywords])
    
    if first_hit:
        print(f" Step 1: Found and clicked '{action.upper()}' target.")
        
        # NYTimes specific: Second layer usually takes a moment to animate
        time.sleep(4) 
        
        # PHASE 2: PRIORITY-BASED CONFIRMATION
        print(" Step 2: Running Priority-Weighted scan (NYTimes Anomaly Check)...")
        # Pass all 3 levels. JS will hunt for Prio 1 before even looking at Prio 2.
        second_hit = attempt_js_click([prio_1, prio_2, prio_3])
        
        if second_hit:
            print(" Step 2: High-priority confirmation clicked!")
        else:
            print("ℹ No secondary confirmation needed. Proceeding to audit.")
            
        time.sleep(2)
        return True
    
    print(" [CONSENT] No matching banner detected.")
    return False