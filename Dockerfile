FROM ubuntu:trusty

####################
# apt-get installs #
####################

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y \
    git-core \
    g++ \
    make \
    python-dev \
    gfortran \
    libatlas-base-dev \
    libjpeg-dev \
    python-numpy \
    python-pandas \
    python-software-properties \
    openjdk-6-jre \
    zlib1g-dev \
    binutils \
    libproj-dev \
    libgeos-dev \
    libxslt1-dev \
    libxml2-dev \
    libmemcached-dev \
    python-lxml \
    libpq-dev \
    rabbitmq-server \
    python-virtualenv \
    nodejs
RUN easy_install pip

################
# pip installs #
################

RUN mkdir -p /app/requirements/
WORKDIR /app
ADD requirements/base.pip /app/requirements/
RUN pip install -r requirements/base.pip

################################
# copy kobocat to docker image #
################################

ADD . /app

CMD ["/bin/bash", "run.sh"]
