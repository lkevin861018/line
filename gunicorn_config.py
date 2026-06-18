import os


workers = int(os.getenv("WEB_CONCURRENCY", "1"))
threads = int(os.getenv("WEB_CONCURRENCY_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
