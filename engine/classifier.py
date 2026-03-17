import re

def identify(domain):
    domain = domain.lower()

    # 1. SPYWARE / FINGERPRINTING / SESSION REPLAY (High Risk)
    # These record mouse movements, keystrokes, and hardware IDs
    spyware_patterns = [
        r"pixel", r"collect", r"track", r"keylog", r"fingerprint", r"canvas",
        r"fullstory", r"hotjar", r"luckyorange", r"clarity", r"inspectlet",
        r"mouseflow", r"clicktale", r"smartlook", r"sessionstack", r"dynatrace",
        r"userway", r"loggly", r"sentry", r"datadog", r"newrelic", r"mixpanel",
        r"quantummetric", r"glassbox", r"contentsquare", r"tealium"
    ]
    
    # 2. MARKETING / ADVERTISING / RETARGETING
    # These follow you across the web to build a buyer profile
    marketing_patterns = [
        r"adsystem", r"doubleclick", r"adservice", r"adnxs", r"amazon-adsystem",
        r"facebook", r"fbevents", r"taboola", r"outbrain", r"ads-twitter",
        r"googlesyndication", r"popads", r"advertising", r"rubiconproject",
        r"pubmatic", r"openx", r"indexww", r"casalemedia", r"adtech", r"yieldmo",
        r"appier", r"criteo", r"rtbhouse", r"bidswitch", r"adform", r"sitescout",
        r"quantserve", r"adroll", r"mediaplex", r"everesttech"
    ]
    
    # 3. ANALYTICS (Medium Risk)
    analytics_patterns = [
        r"google-analytics", r"segment", r"amplitude", r"statcounter", 
        r"analytics", r"scorecardresearch", r"chartbeat", r"parsely", 
        r"kissmetrics", r"woopra", r"heapanalytics", r"gosquared", r"intercom"
    ]

    # 4. FUNCTIONAL / INFRASTRUCTURE
    functional_patterns = [
        r"gstatic", r"googleapis", r"aws", r"cloudfront", r"akamai",
        r"fastly", r"typekit", r"bootstrapcdn", r"jquery", r"stripe",
        r"paypal", r"cloudinary", r"azure", r"disqus", r"recaptcha"
    ]

    for pattern in spyware_patterns:
        if re.search(pattern, domain): return "Spyware/Fingerprinting"
    for pattern in marketing_patterns:
        if re.search(pattern, domain): return "Marketing/Advertising"
    for pattern in analytics_patterns:
        if re.search(pattern, domain): return "Analytics"
    for pattern in functional_patterns:
        if re.search(pattern, domain): return "Functional"

    return "Unclassified Tracker"