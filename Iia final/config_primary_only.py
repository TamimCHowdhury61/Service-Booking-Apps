# Database Configuration for Primary Laptop Only Operation
# This configuration keeps everything in primary database for single laptop testing
# Secondary laptop connection code remains intact anyone can run this in primary laptioo using this

DATABASE_CONFIG = {
    'primary': {
        'host': 'localhost',  # Primary laptop (contains everything for now)
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_primary',
        'port': 3306
    },
    'secondary': {
        'host': '192.168.41.117',  # Secondary laptop (will connect tonight)
        'user': 'root',
        'password': '12345678',
        'database': 'service_booking_secondary',
        'port': 3306
    }
}

# LLM Configuration
LLM_CONFIG = {
    'api_key': 'Use your own api keys ',
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
    },
    'cleaning': {
        'keywords': ['cleaning', 'maid', 'janitorial', 'housekeeping'],
        'priority_skills': ['deep_cleaning', 'office_cleaning', 'residential_cleaning']
    },
    'hvac': {
        'keywords': ['hvac', 'air conditioning', 'heating', 'ventilation'],
        'priority_skills': ['ac_installation', 'heating_repair', 'maintenance']
    },
    'landscaping': {
        'keywords': ['landscaping', 'garden', 'lawn', 'yard'],
        'priority_skills': ['garden_design', 'lawn_care', 'hardscaping']
    },
    'painting': {
        'keywords': ['painting', 'painter', 'wall', 'exterior'],
        'priority_skills': ['interior_painting', 'exterior_painting', 'decorative']
    },
    'automotive': {
        'keywords': ['automotive', 'car', 'vehicle', 'engine'],
        'priority_skills': ['engine_repair', 'transmission', 'diagnostics']
    }

}
