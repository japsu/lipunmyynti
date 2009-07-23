# encoding: utf-8
# vim: shiftwidth=4 expandtab

import os, sys

# XXX hack
import site
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
site.addsitedir(root_path)

#sys.path.append('/usr/local/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'tracon.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
