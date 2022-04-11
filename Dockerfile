FROM jracine/python37-geckodriver:gecko0.23.0_selenium3.14.1

ADD Requirements.txt /opt/minions/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /opt/minions/Requirements.txt

ADD minions.feeder /opt/minions/minions.feeder
ADD minions.common /opt/minions/minions.common

ENV PYTHONPATH=/opt/minions/minions.common
WORKDIR /opt/minions/minions.feeder/

ENTRYPOINT ["python","app.py"]
