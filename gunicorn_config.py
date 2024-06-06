import threading,app,time,requests

def periodic_task():
    stream_status = 'on'
    while True:
        da_url = 'https://linegg.onrender.com/da'
        params = {"stream_status": stream_status}
        stream_status = requests.get(da_url,params=params).text
        # print(stream_status)
        time.sleep(3)
        # print(da_res.status_code)

def on_starting(server):
    # thread = threading.Thread(target=app.periodic_task)
    thread = threading.Thread(target=periodic_task)
    thread.start()



# # gunicorn --threads 2 -c gunicorn_config.py app:app