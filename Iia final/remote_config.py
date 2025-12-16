# Remote MySQL Connection Configuration
# Save this file on both laptops with appropriate IP adjustments

import os
from getpass import getpass

# Get current laptop's IP for automatic detection
def get_local_ip():
    import socket
    try:
        # Create a socket and connect to an external host
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# Auto-detect which laptop this is running on
LOCAL_IP = get_local_ip()

# Configuration for both laptops
DATABASE_CONFIG = {
    # Primary Laptop (Current - 192.168.41.16)
    'primary': {
        'host': '192.168.41.16',  # UPDATE: Replace with actual primary laptop IP
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_primary',
        'port': 3306
    },

    # Secondary Laptop (Remote - 192.168.41.117)
    'secondary': {
        'host': '192.168.41.117',  # UPDATE: Replace with actual secondary laptop IP
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_secondary',
        'port': 3306
    }
}

# Connection settings
CONNECTION_SETTINGS = {
    'connect_timeout': 10,
    'read_timeout': 30,
    'write_timeout': 30,
    'autocommit': True,
    'charset': 'utf8mb4'
}

# Security settings for remote access
SECURITY_CONFIG = {
    'require_secure_transport': False,  # Set to True if using SSL
    'allowed_ips': [
        '192.168.41.16',  # Primary laptop
        '192.168.41.117',  # Secondary laptop
        '127.0.0.1',       # Localhost
        '0.0.0.0'          # All local network (use with caution)
    ]
}

# LLM Configuration
LLM_CONFIG = {
    'api_key': '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',
    'model': 'anthropic/claude-3.5-sonnet',
    'max_tokens': 500,
    'temperature': 0.7,
    'base_url': 'https://openrouter.ai/api/v1/chat/completions'
}

# Service Categories and Weights for Sorting
SERVICE_SORTING_WEIGHTS = {
    'rating': 0.4,
    'availability': 0.3,
    'experience': 0.2,
    'response_time': 0.1
}

# Common Service Types for Enhanced Features
SERVICE_TYPES = {
    'plumber': {
        'keywords': ['plumbing', 'pipe', 'leak', 'drain', 'faucet', 'toilet'],
        'priority_skills': ['pipe_repair', 'leak_detection', 'installation']
    },
    'electrician': {
        'keywords': ['electrical', 'wiring', 'circuit', 'breaker', 'outlet'],
        'priority_skills': ['wiring', 'circuit_repair', 'safety_inspection']
    },
    'carpenter': {
        'keywords': ['woodwork', 'furniture', 'carpentry', 'repair'],
        'priority_skills': ['furniture_repair', 'custom_work', 'installation']
    },
    'house_painter': {
        'keywords': ['painting', 'paint', 'wall', 'color'],
        'priority_skills': ['interior_painting', 'exterior_painting', 'prep_work']
    },
    'mechanic': {
        'keywords': ['automotive', 'car', 'vehicle', 'repair'],
        'priority_skills': ['engine_repair', 'brake_service', 'diagnostics']
    }
}

def get_database_config(laptop_type='auto'):
    """
    Get database configuration for the specified laptop type
    laptop_type: 'primary', 'secondary', or 'auto'
    """
    if laptop_type == 'auto':
        # Auto-detect based on current IP
        if LOCAL_IP == DATABASE_CONFIG['primary']['host']:
            laptop_type = 'primary'
        elif LOCAL_IP == DATABASE_CONFIG['secondary']['host']:
            laptop_type = 'secondary'
        else:
            print(f"Current IP {LOCAL_IP} not found in config. Defaulting to primary.")
            laptop_type = 'primary'

    return DATABASE_CONFIG[laptop_type]

def update_primary_ip(new_ip):
    """Update primary laptop IP address"""
    DATABASE_CONFIG['primary']['host'] = new_ip
    SECURITY_CONFIG['allowed_ips'][0] = new_ip

def update_secondary_ip(new_ip):
    """Update secondary laptop IP address"""
    DATABASE_CONFIG['secondary']['host'] = new_ip
    SECURITY_CONFIG['allowed_ips'][1] = new_ip

if __name__ == "__main__":
    print(f"Detected local IP: {LOCAL_IP}")
    print(f"Primary DB: {DATABASE_CONFIG['primary']['host']}")
    print(f"Secondary DB: {DATABASE_CONFIG['secondary']['host']}")