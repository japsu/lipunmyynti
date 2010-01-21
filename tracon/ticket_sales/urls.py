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

    url(r'stats/$', redirect_to, dict(url='/hallinta/tiedot/'), name="old_stats_url"),

    url(r'hallinta/$', manage_view, name="manage_view"),

    url(r'hallinta/maksut/$', payments_view, name="payments_view"),
    url(r'hallinta/maksut/yksi/$', process_single_payment_view, name="process_single_payment_view"),
    url(r'hallinta/maksut/yksi/vahvista/$', confirm_single_payment_view, name="confirm_single_payment_view"),
    url(r'hallinta/maksut/monta/$', process_multiple_payments_view, name="process_multiple_payments_view"),
    url(r'hallinta/maksut/monta/vahvista/$', confirm_multiple_payments_view, name="confirm_multiple_payments_view"),

    url(r'hallinta/tiedot/$', stats_view, name="stats_view"),

    url(r'kirjaudu/$', 'django.contrib.auth.views.login', dict(template_name="ticket_admin/login.html"), name="login_page"),
    url(r'kirjaudu/ulos/$', 'django.contrib.auth.views.logout', dict(template_name="ticket_admin/logged_out.html"), name="logout_page"),

    url(r'$', redirect_to, dict(url='/tervetuloa/'), name="empty_url"),
)
