#!/usr/bin/env bash
set -e

source /etc/profile

CELERYD_TASK_SOFT_TIME_LIMIT="${CELERYD_TASK_SOFT_TIME_LIMIT:-$((15*60))}"
# Give tasks 1 minute for exception handling and cleanup before killing timed out Celery processes.
CELERYD_TASK_TIME_LIMIT="${CELERYD_TASK_TIME_LIMIT:-$((${CELERYD_TASK_SOFT_TIME_LIMIT}+60))}"

CELERY_DEFAULT_QUEUE="${CELERY_DEFAULT_QUEUE:-default}"

CELERYD_OPTIONS="--loglevel=DEBUG -Q ${CELERY_DEFAULT_QUEUE} --soft-time-limit=${CELERYD_TASK_SOFT_TIME_LIMIT} --time-limit=${CELERYD_TASK_TIME_LIMIT} --maxtasksperchild=5"

cd "${KOBOCAT_SRC_DIR}"

exec /sbin/setuser wsgi python manage.py celeryd $CELERYD_OPTIONS
