FROM fedora:33

ARG VERSION=develop

LABEL maintainer="patrik.smeds@scilifelab.uu.se"
LABEL version=$VERSION
LABEL bclconvert=4.0.3

RUN yum update -y && yum install -y hostname unzip python3-pip python3-virtualenv git gcc-c++

COPY ./local_files/bcl-convert-4.4.6-2.el8.x86_64.rpm /bcl-convert-4.4.6-2.el8.x86_64.rpm

RUN yum install -y --nogpgcheck /bcl-convert-4.4.6-2.el8.x86_64.rpm && rm bcl-convert-4.4.6-2.el8.x86_64.rpm

RUN git clone -b $VERSION https://github.com/clinical-genomics-uppsala/arteria-bclconvert.git

WORKDIR arteria-bclconvert

RUN mkdir -p /fastq /bclconvert_logs /runfolders

RUN pip3 install -e . && pip3 install -r requirements/prod && pip3 install click==8.1.3
