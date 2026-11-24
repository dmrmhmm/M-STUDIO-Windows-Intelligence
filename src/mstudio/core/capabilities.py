"""Feature inventory and implementation boundaries for M / STUDIO."""
FEATURES = (
    ("system_health", "System health engine", "active"),
    ("performance", "Performance monitoring", "sampling foundation"),
    ("error_diagnostics", "Error diagnosis", "rule-based warning classification"),
    ("hardware", "Hardware intelligence", "snapshot foundation"),
    ("storage", "Disk and storage analysis", "system-volume metrics"),
    ("drivers", "Driver and update audit", "read-only inventory foundation"),
    ("security", "Security and privacy center", "read-only Defender/firewall audit foundation"),
    ("ai", "AI-assisted explanations", "planned; optional opt-in provider, no telemetry"),
    ("reports", "Diagnostics reports", "local JSON export and explicit SQLite history"),
    ("maintenance", "Safe maintenance laboratory", "preview only; no execution"),
)
