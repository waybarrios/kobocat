FROM ubuntu:trusty

######################################################################
# Setting up mongodb is a bit of pain.                               #
# http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/ #
######################################################################

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list

RUN apt-get update
RUN apt-get upgrade -y

# mongodb-org-server
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db

# RUN start mongod

# RUN cat /var/log/mongodb/mongod.log

# ####################
# # apt-get installs #
# ####################

# RUN apt-get install -y \
#     git-core \
#     g++ \
#     make \
#     python-dev \
#     gfortran \
#     libatlas-base-dev \
#     libjpeg-dev \
#     python-numpy \
#     python-pandas \
#     python-software-properties \
#     openjdk-6-jre \
#     zlib1g-dev \
#     binutils \
#     libproj-dev \
#     libxslt1-dev \
#     libxml2-dev \
#     libmemcached-dev \
#     python-lxml \
#     libpq-dev \
#     rabbitmq-server \
#     python-virtualenv \
#     nodejs
# RUN easy_install pip

# ################################
# # copy kobocat to docker image #
# ################################

# RUN mkdir /app
# WORKDIR /app
# ADD . /app

# ############################
# # install pip requirements #
# ############################

# RUN pip install -r requirements/base.pip

# CMD ["/bin/bash", "run.sh"]


EXPOSE 27017
CMD ["--port 27017"]
ENTRYPOINT usr/bin/mongod
