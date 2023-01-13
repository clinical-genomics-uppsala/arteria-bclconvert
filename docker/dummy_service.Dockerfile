FROM python:3.9

ARG VERSION=develop

RUN apt update && apt install git

RUN useradd stanley
RUN mkdir /home/stanley
RUN usermod -u 10000 stanley
RUN groupadd -g 2004 wp4
RUN usermod -a -G wp4 stanley

WORKDIR arteria-bclconvert

RUN mkdir -p /fastq /bclconvert-logs /runfolders
RUN chown stanley:root -R /fastq /bclconvert-logs /runfolders /home/stanley

COPY ./bin/bcl-convert /usr/bin/bcl-convert

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install git+https://github.com/clinical-genomics-uppsala/arteria-bclconvert.git@${VERSION}
RUN pip install click==8.1.3
RUN pip install -r https://raw.githubusercontent.com/clinical-genomics-uppsala/arteria-bclconvert/${VERSION}/requirements/prod
WORKDIR /

RUN chown -R stanley:wp4 /opt/venv
