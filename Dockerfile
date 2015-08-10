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
    python-virtualenv
RUN easy_install pip

################
# pip installs #
################

RUN mkdir -p /app/requirements/
WORKDIR /app
ADD requirements/base.pip /app/requirements/
RUN pip install -r requirements/base.pip

#############
# setup npm #
#############

# https://nodesource.com/blog/nodejs-v012-iojs-and-the-nodesource-linux-repositories
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_0.12 | bash -
RUN apt-get install -y nodejs

################################
# copy kobocat to docker image #
################################

ADD . /app

################
# npm installs #
################

RUN npm install -g --save-dev
RUN npm install -g bower karma grunt-cli

CMD ["/bin/bash", "run.sh"]
