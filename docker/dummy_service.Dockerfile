FROM python:3.9

ARG VERSION=dev

RUN apt update && apt install git && git clone -b $VERSION https://github.com/clinical-genomics-uppsala/arteria-bclconvert.git

WORKDIR arteria-bclconvert

RUN mkdir -p /fastq /bclconvert_logs /runfolders

COPY ./bin/bcl-convert //usr/bin/bcl-convert

RUN pip install -e . && pip install -r requirements/prod && pip install click==8.1.3
