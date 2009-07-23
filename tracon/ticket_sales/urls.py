from django.conf.urls.defaults import *

from tracon.ticket_sales.views import *

urlpatterns = patterns('',
    url(r'^', test_view, name="test_view")
)
