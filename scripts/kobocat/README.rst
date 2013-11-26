## Assumptions

- Installing on ubuntu server
- Has the user ubuntu already defined
- With SSH access via a key

## Before Starting

- Change host_string, key_filename, mysql password - currently set to 'kobocat'
  for the install, should be changed later - on fabfile.py.
- necessary changes can also be applied in the setting files in the `files`
  folder as well as init_setup which setups the virtual environment.

## Included:

- fabfile.py - installs using fabric on a freshly installed ubuntu os server
- init_virtualenv - added to .bashrc for virtualenvwrapper
- init_setup - sets up the virtualenv
- files/celeryd - celeryd daemon init.d script
- files/celeryd.default - default celeryd config placed /etc/default/celeryd
- files/kobocat.nginx - nginx server config
- files/uwsgi.conf - uwsgi init script -> /etc/init/uwsgi.conf
- files/uwsgi.ini - uwsgi ini file -> ~/src/kobocat/formhub/uwsgi.ini
- kobocat.py - django settings file -> local_settings.py


# Installation

    pip install fabric
    fab server_setup:default
