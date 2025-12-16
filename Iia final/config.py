# Database Configuration for Distributed System


DATABASE_CONFIG = {
    'primary': {
        'host': 'localhost',  # This laptop (primary)
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_primary',
        'port': 3306
    },
    'secondary': {
        'host': '192.168.41.117',  # Secondary laptop IP
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_secondary',
        'port': 3306
    }
}

# LLM Configuration - Google Gemini API
LLM_CONFIG = {
    "api_key": "USE your own api key",// use your own api key here
    "model": "gemini-2.0-flash-001",  # or gemini-2.5-flash etc.
    "temperature": 0.3,
    "max_tokens": 1024,
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
