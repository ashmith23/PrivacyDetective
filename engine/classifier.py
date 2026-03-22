import re

def identify(domain, path=""):
    domain = domain.lower()
    path = path.lower()
    
    # --- LAYER 1: THE MASTER REGEX (Expanded for 2026 standards) ---
    
    # 1. SPYWARE / FINGERPRINTING / SESSION REPLAY
    spyware_patterns = [
        r"pixel", r"collect", r"track", r"keylog", r"fingerprint", r"canvas",
        r"fullstory", r"hotjar", r"luckyorange", r"clarity", r"inspectlet",
        r"mouseflow", r"clicktale", r"smartlook", r"sessionstack", r"dynatrace",
        r"userway", r"loggly", r"sentry", r"datadog", r"newrelic", r"mixpanel",
        r"quantummetric", r"glassbox", r"contentsquare", r"tealium", r"permutive",
        r"mparticle", r"liadm", r"bounceexchange", r"list-manage", r"pendo",
        r"vitals", r"speedcurve", r"logrocket", r"noibu", r"foresee", r"qualtrics"
    ]
    
    # 2. MARKETING / ADVERTISING / RETARGETING
    marketing_patterns = [
        r"adsystem", r"doubleclick", r"adservice", r"googlesyndication", r"2mdn", r"invitemedia",
        r"facebook", r"fbevents", r"fbcdn", r"messenger", r"amazon-adsystem", r"assoc-amazon",
        r"adnxs", r"taboola", r"outbrain", r"ads-twitter", r"t.co", r"advertising", 
        r"rubiconproject", r"pubmatic", r"openx", r"indexww", r"casalemedia", r"adtech", 
        r"yieldmo", r"appier", r"criteo", r"rtbhouse", r"bidswitch", r"adform", r"sitescout",
        r"quantserve", r"adroll", r"mediaplex", r"everesttech", r"bluekai", r"demdex",
        r"dotomi", r"mathtag", r"tapad", r"impactradius", r"yieldmanager", r"revcontent",
        r"tiktok", r"byteoversea", r"snapchat", r"sc-static", r"pinterest", r"pinimg",
        r"linkedin", r"licdn", r"reddit", r"redditmedia", r"bidtellect", r"gumgum", 
        r"triplelift", r"teads", r"sharethrough", r"zemanta", r"popads", r"propellerads"
    ]
    
    # 3. ANALYTICS (Behavioral Tracking)
    analytics_patterns = [
        r"google-analytics", r"segment", r"amplitude", r"statcounter", 
        r"analytics", r"scorecardresearch", r"chartbeat", r"parsely", 
        r"kissmetrics", r"woopra", r"heapanalytics", r"gosquared", r"intercom",
        r"optimizely", r"vwo", r"crazyegg", r"hubspot", r"marketo", r"pardot",
        r"braze", r"iterable", r"customer.io", r"posthog", r"snowplow", r"drift"
    ]

    # 4. FUNCTIONAL / INFRASTRUCTURE
    functional_patterns = [
        r"gstatic", r"googleapis", r"aws", r"cloudfront", r"akamai",
        r"fastly", r"typekit", r"bootstrapcdn", r"jquery", r"stripe",
        r"paypal", r"cloudinary", r"azure", r"disqus", r"recaptcha",
        r"wp.com", r"wordpress", r"gravatar", r"shopify", r"bigcommerce",
        r"wix", r"squarespace", r"edgecast", r"limelight", r"stackpath",
        r"unpkg", r"jsdelivr", r"cdnjs", r"font-awesome", r"google-fonts", r"maps.apple"
    ]

    # --- PHASE 1: EXACT PATTERN MATCHING ---
    for pattern in spyware_patterns:
        if re.search(pattern, domain): return "Spyware/Fingerprinting"
    for pattern in marketing_patterns:
        if re.search(pattern, domain): return "Marketing/Advertising"
    for pattern in analytics_patterns:
        if re.search(pattern, domain): return "Analytics"
    for pattern in functional_patterns:
        if re.search(pattern, domain): return "Functional"

    # --- PHASE 2: ADVANCED BEHAVIORAL HEURISTICS ---
    
    # 1. Obfuscated Unique IDs (Entropy Check)
    # Detects long random strings used for Cross-Site Tracking
    if re.search(r'[a-f0-9]{24,}', path) or re.search(r'[a-f0-9-]{32,}', path):
        return "Inferred: High-Risk Tracker (Unique ID Found)"

    # 2. Tracking Endpoint Signatures
    # Common path structures for headless tracking pings
    tracking_endpoints = [
        r"/v\d/t", r"/v\d/e", r"/event", r"/track", r"/collect", 
        r"/pixel", r"/ping", r"/notify", r"/log", r"/beacons"
    ]
    for ep in tracking_endpoints:
        if re.search(ep, path):
            return "Inferred: Analytics (Endpoint Match)"

    # 3. Parameter-Based Fingerprinting Identification
    # Looks for data-mining keys in the query string
    fp_params = ['canvas=', 'webgl=', 'font=', 'audio=', 'rects=', 'plugin=']
    if any(p in path for p in fp_params):
        return "Inferred: Fingerprinting (Hardware Probe)"

    # 4. Ad-Tech "Sync" Signatures
    if any(key in path for key in ['/cm', '/sync', 'user_id', 'match', 'bidder', 'cookie-sync']):
        return "Inferred: Ad-Sync (Marketing)"

    # 5. Infrastructure Check
    if any(key in domain for key in ['cdn.', 'static.', 'assets.', 'images.', 'fonts.', 's3.', 'edge.']):
        return "Inferred: Infrastructure (Functional)"

    # 6. API & Backend
    if any(key in domain for key in ['api.', 'graphql.', 'rpc.', 'socket.', 'v1.']):
        return "Inferred: API/Backend (Functional)"

    # 7. Performance & Telemetry
    if any(key in domain or key in path for key in ['telemetry', 'log-', 'metric', 'error', 'crash', 'report']):
        return "Inferred: Performance (Analytics)"

    return "Unclassified Tracker"

def get_brand(domain):
    """
    Enhanced Canonical Mapping to group umbrella brands.
    """
    domain = domain.lower()
    
    mapping = {
        "google": ["google", "gstatic", "doubleclick", "googlesyndication", "2mdn", "youtube", "ggpht", "googleapis"],
        "meta": ["facebook", "fbcdn", "fbevents", "instagram", "cdninstagram", "whatsapp"],
        "amazon": ["amazon", "amazonaws", "media-amazon", "amazon-adsystem", "assoc-amazon"],
        "microsoft": ["microsoft", "bing", "clarity", "azure", "live.com", "office", "skype"],
        "tiktok": ["tiktok", "byteoversea", "ibyteimg", "musical.ly"],
        "adobe": ["adobe", "demdex", "typekit", "omtrdc"],
        "apple": ["apple", "mzstatic", "icloud"]
    }
    
    for brand, patterns in mapping.items():
        if any(p in domain for p in patterns):
            return brand
                
    # Fallback Logic
    parts = domain.split('.')
    if len(parts) >= 2:
        brand = parts[-2]
        if brand in ['com', 'net', 'org', 'co', 'in', 'edu', 'gov', 'io', 'me', 'tech'] and len(parts) >= 3:
            brand = parts[-3]
        return brand
    return "independent"

def get_risk_metadata(category):
    """
    Returns (risk_weight, severity_label) based on the classified category.
    """
    cat = category.lower()
    
    if "spyware" in cat or "fingerprinting" in cat or "high-risk" in cat:
        return 10, "CRITICAL"
    if "marketing" in cat or "ad-sync" in cat:
        return 7, "HIGH"
    if "analytics" in cat or "performance" in cat:
        return 4, "MEDIUM"
    if "functional" in cat or "infrastructure" in cat or "api" in cat:
        return 1, "LOW"
    
    return 5, "UNSPECIFIED" # Default for Unclassified

def calculate_compliance_score(trackers):
    if not trackers:
        return 100
    
    total_weighted_risk = 0
    for t in trackers:
        risk_weight, _ = get_risk_metadata(t['category'])
        total_weighted_risk += risk_weight
    
    # Penalty-based scoring formula:
    # We subtract risk from 100. More trackers + higher risk = lower score.
    # We use a logarithmic-style dampening so one tracker doesn't zero the score.
    score = 100 - (total_weighted_risk * 1.5)
    return max(0, min(100, int(score)))