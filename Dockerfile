FROM ubuntu:16.04

RUN apt-get -y update

WORKDIR /serverstats

ADD . /serverstats

RUN apt-get install python-pip -y

RUN pip install .

CMD ["serverstats", "run"]
