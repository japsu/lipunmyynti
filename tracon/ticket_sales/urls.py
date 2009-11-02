# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from tracon.ticket_sales.views import *

urlpatterns = patterns('',
    url(r'^welcome/$', welcome_view, name="welcome_phase"),
    url(r'^tickets/$', tickets_view, name="tickets_phase"),
    url(r'^shirts/$', shirts_view, name="shirts_phase"),
    url(r'^address/$', address_view, name="address_phase"),
    url(r'^confirm/$', confirm_view, name="confirm_phase"),
    url(r'^thanks/$', thanks_view, name="thanks_phase"),

    url(r'^', redirect_to, dict(url='/welcome/'), name="empty_url"),
)
