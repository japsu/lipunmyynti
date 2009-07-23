# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *

from tracon.ticket_sales.views import *

urlpatterns = patterns('',
    url(r'^welcome/$', welcome_view, name="welcome_view"),
    url(r'^tickets/$', tickets_view, name="tickets_view"),
    url(r'^shirts/$', shirts_view, name="shirts_view"),
    url(r'^address/$', address_view, name="address_view"),
    url(r'^confirm/$', confirm_view, name="confirm_view"),
    url(r'^thanks/$', thanks_view, name="thanks_view"),

    url(r'^', welcome_view, name="empty_url")
)
