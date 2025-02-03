# Include all global variables in this file.
# These are used across different modules/packages
# where required.

# Service Name
SVC_NAME = 'batman-ms-orchestrator'

# DB Settings
DB_HOST_WRITER = '127.0.0.1'
DB_HOST_READER = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'batman_orchestrator'
DB_USER = 'root'
DB_PASS = ''

# Requests settings
REQUESTS_LIMIT = 10

# Sentry Settings
SENTRY_DSN = ''
SENTRY_TRACES_SAMPLE_RATE = 1.0
SENTRY_PROFILES_SAMPLE_RATE = 1.0
SENTRY_ENV = 'production'

# Flask Settings
FLASK_PORT = 80
FLASK_DEBUG = False