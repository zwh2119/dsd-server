FROM python:3.7

MAINTAINER Wenhui Zhou

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["/usr/bin/env", "python3", "init_db.py"]

CMD ["gunicorn", "cloud_server:app", "-c", "./gunicorn.conf.py"]