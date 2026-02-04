"""
Example configurations for Network Impairment Tool
Save these as reference for common testing scenarios
"""

# ============================================================================
# Gaming Latency Simulation
# ============================================================================
GAMING_HIGH_LATENCY = {
    "filter_str": "outbound and udp",
    "lag_enabled": True,
    "lag_ms": 200,
    "drop_enabled": True,
    "drop_chance": 3.0,
    "throttle_enabled": False,
    "duplicate_enabled": False,
    "out_of_order_enabled": True,
    "out_of_order_chance": 10.0,
    "tamper_enabled": False,
}

# ============================================================================
# Poor WiFi Conditions
# ============================================================================
POOR_WIFI = {
    "filter_str": "outbound",
    "lag_enabled": True,
    "lag_ms": 150,
    "drop_enabled": True,
    "drop_chance": 8.0,
    "throttle_enabled": True,
    "throttle_ms": 30,
    "throttle_chance": 40.0,
    "duplicate_enabled": True,
    "duplicate_count": 1,
    "duplicate_chance": 5.0,
    "out_of_order_enabled": True,
    "out_of_order_chance": 15.0,
    "tamper_enabled": False,
}

# ============================================================================
# Mobile Network (3G/4G)
# ============================================================================
MOBILE_NETWORK = {
    "filter_str": "outbound and tcp",
    "lag_enabled": True,
    "lag_ms": 100,
    "drop_enabled": True,
    "drop_chance": 2.0,
    "throttle_enabled": True,
    "throttle_ms": 50,
    "throttle_chance": 50.0,
    "duplicate_enabled": False,
    "out_of_order_enabled": True,
    "out_of_order_chance": 20.0,
    "tamper_enabled": False,
}

# ============================================================================
# Network Congestion
# ============================================================================
NETWORK_CONGESTION = {
    "filter_str": "tcp",
    "lag_enabled": True,
    "lag_ms": 50,
    "drop_enabled": False,
    "throttle_enabled": True,
    "throttle_ms": 100,
    "throttle_chance": 60.0,
    "duplicate_enabled": False,
    "out_of_order_enabled": True,
    "out_of_order_chance": 30.0,
    "tamper_enabled": False,
}

# ============================================================================
# Data Corruption Testing
# ============================================================================
DATA_CORRUPTION = {
    "filter_str": "outbound and udp",
    "lag_enabled": False,
    "drop_enabled": True,
    "drop_chance": 5.0,
    "throttle_enabled": False,
    "duplicate_enabled": True,
    "duplicate_count": 1,
    "duplicate_chance": 10.0,
    "out_of_order_enabled": False,
    "tamper_enabled": True,
    "tamper_chance": 8.0,
}

# ============================================================================
# Satellite Internet
# ============================================================================
SATELLITE_INTERNET = {
    "filter_str": "outbound",
    "lag_enabled": True,
    "lag_ms": 500,  # High latency typical of satellite
    "drop_enabled": True,
    "drop_chance": 1.0,
    "throttle_enabled": True,
    "throttle_ms": 20,
    "throttle_chance": 30.0,
    "duplicate_enabled": False,
    "out_of_order_enabled": True,
    "out_of_order_chance": 10.0,
    "tamper_enabled": False,
}

# ============================================================================
# Heavy Load Stress Test
# ============================================================================
STRESS_TEST = {
    "filter_str": "tcp",
    "lag_enabled": True,
    "lag_ms": 200,
    "drop_enabled": True,
    "drop_chance": 15.0,  # High drop rate
    "throttle_enabled": True,
    "throttle_ms": 100,
    "throttle_chance": 80.0,  # High throttle rate
    "duplicate_enabled": True,
    "duplicate_count": 3,  # Multiple duplicates
    "duplicate_chance": 20.0,
    "out_of_order_enabled": True,
    "out_of_order_chance": 40.0,
    "tamper_enabled": True,
    "tamper_chance": 10.0,
}

# ============================================================================
# Minimal Impairment (Baseline)
# ============================================================================
MINIMAL = {
    "filter_str": "outbound and udp",
    "lag_enabled": True,
    "lag_ms": 10,
    "drop_enabled": False,
    "throttle_enabled": False,
    "duplicate_enabled": False,
    "out_of_order_enabled": False,
    "tamper_enabled": False,
}

# ============================================================================
# VoIP Quality Testing
# ============================================================================
VOIP_TEST = {
    "filter_str": "outbound and udp and udp.DstPort == 5060",
    "lag_enabled": True,
    "lag_ms": 30,  # VoIP sensitive to latency
    "drop_enabled": True,
    "drop_chance": 1.0,  # Low drop rate
    "throttle_enabled": False,
    "duplicate_enabled": True,
    "duplicate_count": 1,
    "duplicate_chance": 2.0,
    "out_of_order_enabled": True,
    "out_of_order_chance": 5.0,
    "tamper_enabled": False,
}

# ============================================================================
# Video Streaming Test
# ============================================================================
VIDEO_STREAMING = {
    "filter_str": "outbound and tcp and tcp.DstPort == 443",
    "lag_enabled": True,
    "lag_ms": 50,
    "drop_enabled": True,
    "drop_chance": 3.0,
    "throttle_enabled": True,
    "throttle_ms": 30,
    "throttle_chance": 40.0,
    "duplicate_enabled": False,
    "out_of_order_enabled": True,
    "out_of_order_chance": 15.0,
    "tamper_enabled": False,
}

# ============================================================================
# Usage Example
# ============================================================================

"""
To use these configurations:

1. Copy the entire dict
2. In Network Impairment Tool UI, manually set the values
3. Or programmatically in main.py:

    from examples import GAMING_HIGH_LATENCY
    engine.update_config(GAMING_HIGH_LATENCY)
    engine.start()

For testing server-side:

    import requests
    import json
    from examples import GAMING_HIGH_LATENCY
    
    response = requests.post(
        'http://127.0.0.1:5000/api/config',
        json=GAMING_HIGH_LATENCY
    )
    
    requests.post('http://127.0.0.1:5000/api/start')
"""
