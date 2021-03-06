# Django settings for lipunmyynti project.

import os

import django.conf.global_settings as defaults

def mkpath(*parts):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', *parts))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'development.sqlite3',   # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fi'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = mkpath('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = mkpath('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+@)+n!)a=by12)*x5eh0qq10drwe^j^pi!!7@a3j=yc-1@!@zp'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lipunmyynti.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'lipunmyynti.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = defaults.TEMPLATE_CONTEXT_PROCESSORS + (
    'ticket_sales.context_processors.tracon_specific',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'gunicorn',
    'south',
    'pipeline',
    'crispy_forms',
    'ticket_sales',
    'payments'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

USE_X_FORWARDED_HOST = True

EMAIL_HOST='smtp.b2.fi'
DATE_FORMAT='d.m.Y'
PLAIN_CONTACT_EMAIL='liput@tracon.fi'
DEFAULT_FROM_EMAIL="Traconin lipunmyynti <{PLAIN_CONTACT_EMAIL}>".format(**locals())
TICKET_SPAM_EMAIL='Santtu Pajukanta <japsu@tracon.fi>'

LOGIN_URL='/kirjaudu/'
#ANALYTICS_ACCOUNT="UA-21225387-3"
#ANALYTICS_ACCOUNT="UA-00000000-0"

PIPELINE_CSS = {
    'default': {
        'source_filenames': (
          'bootstrap/css/bootstrap.css',
          'bootstrap/css/bootstrap-responsive.css',
          'newstyle.styl'
        ),
        'output_filename': 'default.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}

PIPELINE_JS = {
    'default': {
        'source_filenames': (
          #'jquery-1.8.3.js',
          #'bootstrap/js/bootstrap.js'
        ),
        'output_filename': 'default.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.stylus.StylusCompiler',
)

PIPELINE_STYLUS_BINARY = 'stylus' # hail PATH

# XXX
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

SHOP_TITLE = 'Traconin lippukauppa'
EVENT_NAME = 'Tracon 8'
EVENT_HEADLINE = 'Tampere-talossa 14.-15. syyskuuta 2013'
EVENT_NAME_GENITIVE = 'Tracon 8:n'
EVENT_NAME_ILLATIVE = 'Tracon 8:aan'
EVENT_URL = 'http://2013.tracon.fi'

SHIPPING_AND_HANDLING_CENTS = 150
DUE_DAYS = 7
LOW_AVAILABILITY_THRESHOLD = 10

from payments.defaults import CHECKOUT_PARAMS
CHECKOUT_PARAMS = dict(CHECKOUT_PARAMS, 
    PASSWORD='SAIPPUAKAUPPIAS', # test account
    MERCHANT='375917', # test account
    RETURN='http://localhost:8000/process/', # XXX
    DELIVERY_DATE='20130914' # Tracon 8 start
)

REFERENCE_NUMBER_TEMPLATE = "8{:04d}"