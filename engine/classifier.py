# trackers categorization.

TRACKER_WORDS = {
    "MARKETING": ["ads", "doubleclick", "googlead", "amazon-ad", "pixel", "facebook", "marketing", "adsystem"],
    "ANALYTICS": ["analytics", "scorecard", "stats", "track", "metrics", "collect", "log", "chartbeat"],
    "SOCIAL": ["twitter", "linkedin", "instagram", "tiktok", "t.co"],
    "INFRA_CDN": ["gstatic", "googleapis", "cloudfront", "akamai", "fastly", "msecnd"]
}

def identify(url):
    url = url.lower()
    for cat, keys in TRACKER_WORDS.items():
        if any(k in url for k in keys):
            return cat
    return "POTENTIAL_TRACKER"