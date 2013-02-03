# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),
    url(r'^', include('tracon.ticket_sales.urls'))
)
