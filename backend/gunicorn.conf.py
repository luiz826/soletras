import multiprocessing
import os

# Server configuration
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = 'sync'

# Timeouts (important for SpaCy processing)
timeout = 120
graceful_timeout = 30

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Preload app for better memory usage
preload_app = True
