export DJANGO_SETTINGS_MODULE="kobocat_settings"

python manage.py syncdb --noinput
python manage.py migrate
git clone https://github.com/kobotoolbox/kobocat-template.git
python manage.py collectstatic --noinput

# To actually use the server you have to create a site and super user.
# from django.contrib.sites.models import Site
# Site.objects.create(domain='test', name='Test')
# python manage.py createsuperuser

# gunicorn onadata.apps.main.wsgi:application -w 2 -b :8000
source default_env.source.bash && uwsgi -d uwsgi.ini