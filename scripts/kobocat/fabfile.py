import os
import sys

from fabric.api import env, run, cd, sudo, put


DEPLOYMENTS = {
    'default': {
        'home': '/home/ubuntu/src/',
        'host_string':
        'ubuntu@ec2-54-200-151-185.us-west-2.compute.amazonaws.com',
        'project': 'kobocat',
        'key_filename': os.path.expanduser('~/.ssh/kobo01.pem'),
        'virtualenv': '/home/ubuntu/.virtualenvs/kobocat'
    },
}


def run_in_virtualenv(command):
    d = {
        'activate': os.path.join(
            env.virtualenv, 'bin', 'activate'),
        'command': command,
    }
    run('source %(activate)s && %(command)s' % d)


def check_key_filename(deployment_name):
    if 'key_filename' in DEPLOYMENTS[deployment_name] and \
       not os.path.exists(DEPLOYMENTS[deployment_name]['key_filename']):
        print "Cannot find required permissions file: %s" % \
            DEPLOYMENTS[deployment_name]['key_filename']
        return False
    return True


def setup_env(deployment_name):
    env.update(DEPLOYMENTS[deployment_name])
    if not check_key_filename(deployment_name):
        sys.exit(1)
    env.code_src = os.path.join(env.home, env.project)
    env.pip_requirements_file = os.path.join(env.code_src, 'requirements.pip')


def server_setup(deployment_name):
    setup_env(deployment_name)
    sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db')
    sudo('su - -c "%s"' % "echo 'deb http://ftp.osuosl.org/pub/mariadb/repo/5.5/ubuntu precise main' | tee /etc/apt/sources.list.d/mariadb.list")
    sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
    sudo('su - -c "%s"' % "echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list")
    sudo('apt-get update')

    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password kobocat'")
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password kobocat'")

    sudo('apt-get -y --force-yes install libssl-dev default-jre gcc git python-dev python-setuptools python-distribute libjpeg-dev libfreetype6-dev zlib1g-dev rabbitmq-server build-essential libxslt1-dev mongodb-10gen mariadb-client libmariadbclient18 libmariadbclient-dev mariadb-server mlocate vim net-tools sudo nginx')
    sudo('easy_install pip')
    sudo('pip install virtualenvwrapper uwsgi')

    sudo('ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/')
    sudo('ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/')
    sudo('ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/')

    sudo('echo "CREATE USER \'kobocat\'@\'%\' IDENTIFIED BY \'kobocat\';\q" | mysql -u root -pkobocat')
    sudo('echo "GRANT ALL PRIVILEGES ON *.* TO \'kobocat\'@\'%\';FLUSH PRIVILEGES;\q" | mysql -u root -pkobocat')
    sudo('echo "CREATE DATABASE kobocat;\q" | mysql -u kobocat -pkobocat')

    run('mkdir -p src')
    with cd('~/src'):
        run('git clone https://github.com/kobotoolbox/kobocat.git')
    with cd('~/src/kobocat/'):
        run('git submodule init')
        run('git submodule update')

    run('mkdir -p ~/deploy')
    with cd('~/deploy'):
        put('./files/*', '~/deploy/')
        sudo('cp celeryd /etc/init.d/celeryd')
        sudo('chmod +x /etc/init.d/celeryd')
        sudo('update-rc.d celeryd defaults')
        sudo('cp celeryd.default /etc/default/celeryd')
        sudo('cp kobocat.nginx /etc/nginx/sites-available/default')
        sudo('cp uwsgi.conf /etc/init/uwsgi.conf')
        run('cp uwsgi.ini /home/ubuntu/src/kobocat/formhub/uwsgi.ini')
        run('cp kobocat.py /home/ubuntu/src/kobocat/formhub/local_settings.py')
        sudo('ln -s /lib/init/upstart-job /etc/init.d/uwsgi')

    put('init_virtualenv', '~/.init_virtualenv')
    put('init_setup', '~/.init_setup')
    run('source ~/.init_setup')
    run('echo "export DJANGO_SETTINGS_MODULE=formhub.settings" >> ~/.bashrc')

    with cd('~/src/kobocat/'):
        run_in_virtualenv('pip install -r requirements.pip')
        run_in_virtualenv('pip install -r requirements-ses.pip')
        run_in_virtualenv('pip install -r requirements-s3.pip')
        run_in_virtualenv('pip install -r requirements-mysql.pip')

        run('export DJANGO_SETTINGS_MODULE=formhub.settings')
        run_in_virtualenv("python manage.py syncdb --noinput --settings='formhub.settings'")
        run_in_virtualenv("python manage.py migrate --settings='formhub.settings'")
        run_in_virtualenv("python manage.py collectstatic --noinput --settings='formhub.settings'")

    sudo('/etc/init.d/nginx restart')
    sudo('/etc/init.d/celeryd restart')
    sudo('mkdir -p /var/log/uwsgi')
    sudo('chown -R ubuntu /var/log/uwsgi')
    sudo('start uwsgi')
