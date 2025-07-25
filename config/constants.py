"""
Constants and static values for the Google AI Studio Proxy
"""

# Safety settings for Google AI
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH", 
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# Available models
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro"
]

# Default model
DEFAULT_MODEL = "gemini-2.5-flash"

# Tunnel providers
TUNNEL_PROVIDERS = ["Ngrok", "Cloudflare", "LocalTunnel"]

# Bypass levels
BYPASS_LEVELS = ["none", "light", "medium", "strong", "extreme"]

# Default generation config
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "maxOutputTokens": 20000,
    "topP": 0.9,
    "topK": 45,
    "frequencyPenalty": 0.0,
    "presencePenalty": 0.0
}

# HTTP status codes
HTTP_STATUS = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500
}

# Response formats
RESPONSE_FORMATS = {
    "STREAMING": "text/plain",
    "JSON": "application/json"
}

# Logging levels
LOG_LEVELS = {
    "DEBUG": "debug",
    "INFO": "info", 
    "WARNING": "warning",
    "ERROR": "error",
    "SUCCESS": "success"
}

# Message roles
MESSAGE_ROLES = {
    "USER": "user",
    "ASSISTANT": "assistant",
    "SYSTEM": "system",
    "MODEL": "model"
}

# Content types
CONTENT_TYPES = {
    "TEXT": "text",
    "JSON": "application/json"
}
