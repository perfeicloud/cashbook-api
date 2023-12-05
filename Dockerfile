FROM python:slim
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
 && pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
 && pip install --no-cache-dir --upgrade pip setuptools \
 && pip install --no-cache-dir --upgrade gevent gevent-websocket gunicorn \
    Flask>=3.0.0 \
    Flask-SQLAlchemy>=3.1.1 \
    mysql-connector-python>=8.2.0 \
    requests>=2.31.0 \
    authlib>=1.2.1 \
    redis>=5.0.1 
ENTRYPOINT ["gunicorn","app:app","-c"]

##############################################################
#1.  docker build -f ./Dockerfile -t gunicorn .
#
#2.  docker run -d --restart=always -p 127.0.0.1:8000:8000 \
#      -v /var/run/:/var/run/ \
#      -v /etc/localtime:/etc/localtime \
#      -v /home/cashbook-api:/home/cashbook-api \
#      --name cashbook-api -w /home/cashbook-api \
#      gunicorn ./gunicorn.conf.py
##############################################################