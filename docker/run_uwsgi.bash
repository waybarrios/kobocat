#!/usr/bin/env bash
set -e

source /etc/profile

KOBOCAT_WEB_SERVER="${KOBOCAT_WEB_SERVER:-uWSGI}"
if [[ "${KOBOCAT_WEB_SERVER^^}" == 'UWSGI' ]]; then
    exec /sbin/setuser wsgi /usr/local/bin/uwsgi --ini "${KOBOCAT_SRC_DIR}/docker/kobocat.ini"
else
    cd "${KOBOCAT_SRC_DIR}"

    pip install werkzeug ipython
    exec python manage.py runserver_plus 0:8000
fi
