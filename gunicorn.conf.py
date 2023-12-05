import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'   # *sync|eventlet|gevent...
# reload = True
#pidfile = '/var/run/gunicorn.pid'
loglevel = 'warning'   # debug|*info|warning|error|critical
#access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
#accesslog = '/var/log/gunicorn/access.log'
#errorlog = '/var/log/gunicorn/error.log'
