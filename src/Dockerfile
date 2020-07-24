FROM centos:centos7

# set work dir
WORKDIR /usr/src/app

# env vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8

RUN set -eux \
    yum -y update \
    && yum -y install curl bzip2 \
    && yum -y install libressl-dev libffi-dev gcc musl-dev libgeos-dev \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local/ \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3 \
    && conda update conda \
    # && conda install -y /usr/src/app/requirements.txt \
    && conda install -c conda-forge fastapi uvicorn python-multipart \
        geopandas pytest requests \
    && conda clean --all --yes \
    && rpm -e --nodeps curl bzip2 \
    && yum clean all


# copy project
COPY . /usr/src/app
