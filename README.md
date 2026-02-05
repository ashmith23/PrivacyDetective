Privacy Detective: A Web Based System for observing Third Party Runtime Behavior and Consent Gaps in Modern Websites.

Privacy Detective is an end-to-end, dynamic auditing framework designed to expose "Privacy Theater." It specializes in detecting the gap between User Intent (clicking "Reject") and Network Reality (actual tracking behavior).
By automating the penetration of complex Dark Patterns and analyzing real-time network telemetry, the system calculates a quantitative Privacy Delta to score a website's regulatory compliance.

Project Architecture:

The system is divided into five specialized modules that work in a sequential pipeline:
M1: Cold Start Protocol: Manages session isolation to ensure no "residual" cookies or cache interfere with the audit.
M2: Interaction Engine: Features a recursive JS Bridge to handle multi-layered iframes and a 3-Level Priority Heuristic for button identification.
M3: Network Sniffer: Intercepts full-stack HTTP/HTTPS traffic to log every script, pixel, and beacon.
M4: Traffic Classifier: Categorizes domains into Trackers, Infra CDNs, and Consent Overhead using real-time URL analysis.
M5: Delta Engine: Performs the comparative analysis between Accept and Reject flows to generate the final Compliance Score.

Key Features:

Weighted Heuristic Scanning: Prioritizes "Hard Rejections" (Level 1) over "Save" buttons (Level 2) to bypass deceptive UI traps.
Comparative Delta Metric: Our signature metric that proves compliance by measuring how many trackers ignore a rejection signal.
Retaliatory (Spite) Tracker Detection: Identifies fingerprinting scripts that trigger exclusively when consent is denied.
Infrastructure Awareness: Automatically filters out CDNs and essential libraries to reduce "noise" in compliance reports.

Sample Findings:

In real-world testing (e.g., NYTimes), the engine has uncovered that even when a user successfully navigates a multi-step "Reject" flow:
86% of trackers typically remain active.
4 unique domains often appear only in the "Reject" flow (Consent Overhead & Fingerprinting).
Dark Patterns are systematically used to hide the "Reject All" button within nested iframes.

Tech Stack:

Language: Python 3.x
Automation: Selenium / Webdriver
Network Interception: Selenium-wire / Proxy-man
Frontend Logic: Custom JavaScript Injection (JS Bridge)
Analysis: Heuristic Data Processing

