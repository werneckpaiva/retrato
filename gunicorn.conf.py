import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
# accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'error'
capture_output = True
enable_stdio_inheritance = True
timeout = 60
daemon = False

