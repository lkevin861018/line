import threading
import app

def on_starting(server):
    thread = threading.Thread(target=app.periodic_task)
    thread.start()

# # gunicorn --threads 2 -c gunicorn_config.py app:app