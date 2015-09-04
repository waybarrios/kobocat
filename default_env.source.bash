export KOBOFORM_URL=${KOBOFORM_URL:-"koboform"} # TODO: Move this default to the code and separate into internal and external URLs.
export KOBOCAT_SRC=${KOBOCAT_SRC:-$(dirname $(readlink -f $BASH_SOURCE))}
export KOBOCAT_UWSGI_SOCKET=${KOBOCAT_UWSGI_SOCKET:-0.0.0.0:3031}