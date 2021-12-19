FROM continuumio/anaconda3:2020.07

RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y g++
RUN apt-get install -y libfontconfig


ADD Requirements.txt /opt/minions/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /opt/minions/Requirements.txt

ADD minions.feeder /opt/minions/minions.feeder
ADD minions.common /opt/minions/minions.common

ADD phantomjs-2.1.1-linux-x86_64 /opt/phantomjs-2.1.1-linux-x86_64

ENV PYTHONPATH=/opt/minions/minions.common
ENV PATH=$PATH:/opt/phantomjs-2.1.1-linux-x86_64/bin
ENV OPENSSL_CONF=/etc/ssl/
WORKDIR /opt/minions/minions.feeder/

ENTRYPOINT ["python","app.py"]
