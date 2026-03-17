from engine.classifier import identify

class DeltaEngine:
    def __init__(self, accept_logs, reject_logs):
        # Using sets automatically removes duplicates for clean math
        self.accept_set = set(accept_logs)
        self.reject_set = set(reject_logs)

    def generate_report(self):
        # 1. LEAKAGE: Trackers that ignored the 'Reject' command
        # (They exist in both sets and are classified as violations)
        leakage = [url for url in self.reject_set.intersection(self.accept_set) 
                   if identify(url) == "TRACKER_VIOLATION"]

        # 2. UNIQUE TO REJECT: Domains that only appear when you try to opt-out
        unique_to_reject = self.reject_set - self.accept_set
        
        # 3. SCORE CALCULATION
        # We define 'Total Potential Trackers' as everything found in the 'Accept' flow
        accept_trackers = [url for url in self.accept_set if identify(url) == "TRACKER_VIOLATION"]
        total_count = len(accept_trackers)
        
        if total_count == 0:
            compliance_score = 100.0
        else:
            leaked_count = len(leakage)
            # Math: (1 - (Failure Rate)) * 100
            compliance_score = max(0.0, (1 - (leaked_count / total_count)) * 100)

        return {
            "score": f"{compliance_score:.1f}%",
            "total_trackers_found": total_count,
            "leaked_trackers": leakage,
            "overhead_detected": [url for url in unique_to_reject if identify(url) == "CONSENT_OVERHEAD"],
            "suspicious_unique": [url for url in unique_to_reject if identify(url) == "TRACKER_VIOLATION"]
        }

# STANDALONE FUNCTION (The 'Plug-and-Play' helper)
def get_delta_report(accept_logs, reject_logs):
    engine = DeltaEngine(accept_logs, reject_logs)
    return engine.generate_report()