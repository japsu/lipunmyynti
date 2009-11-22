# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from tracon.ticket_sales.views import *

urlpatterns = patterns('',
    url(r'tervetuloa/$', welcome_view, name="welcome_phase"),
    url(r'liput/$', tickets_view, name="tickets_phase"),
    url(r'paidat/$', shirts_view, name="shirts_phase"),
    url(r'toimitusosoite/$', address_view, name="address_phase"),
    url(r'vahvistus/$', confirm_view, name="confirm_phase"),
    url(r'kiitos/$', thanks_view, name="thanks_phase"),

    url(r'$', redirect_to, dict(url='/tervetuloa/'), name="empty_url"),
)
