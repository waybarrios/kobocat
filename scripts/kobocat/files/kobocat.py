from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'localhost:3030',
    'localhost:8000',
]

# choose a different database...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kobocat',
        'USER': 'kobocat',
        'PASSWORD': 'kobocat',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}
# Make a unique unique key just for testing, and don't share it with anybody.
SECRET_KEY = 'g[3=+P5iG.4980+2-AQex(fSm2-OX*-YQCfzAQ?5g#DgpWy1$KsCbe[>Y5rkoV'

# GOOGLE_SITE_VERIFICATION = ''
# GOOGLE_ANALYTICS_PROPERTY_ID = ''
# GOOGLE_ANALYTICS_DOMAIN = ''

#INSTALLED_APPS += ('django_extensions',)

CORS_ORIGIN_WHITELIST = ()

MONGO_DATABASE = {
    'HOST': '127.0.0.1',
    'PORT': 27017,
    'NAME': 'kobocat',
    'USER': '',
    'PASSWORD': ''
}

# celery
BROKER_BACKEND = "rabbitmq"
BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672/'
CELERY_RESULT_BACKEND = "amqp"  # telling Celery to report results to RabbitMQ
CELERY_ALWAYS_EAGER = False


TESTING_MODE = False
if len(sys.argv) >= 2 and (sys.argv[1] == "test" or sys.argv[1] == "test_all"):
    # This trick works only when we run tests from the command line.
    TESTING_MODE = True
else:
    TESTING_MODE = False

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    subprocess.call(["rm", "-r", MEDIA_ROOT])
    MONGO_DATABASE['NAME'] = "formhub_test"
    # need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
    # to run tasks immediately while testing
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'
    ENKETO_API_TOKEN = 'abc'
    #TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
else:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

if PRINT_EXCEPTION and DEBUG:
    MIDDLEWARE_CLASSES += ('utils.middleware.ExceptionLoggingMiddleware',)
# Clear out the test database
if TESTING_MODE:
    MONGO_DB.instances.drop()
