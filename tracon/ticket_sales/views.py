from django.shortcuts import render_to_response
from django.template import RequestContext

def test_view(request):
    vars = RequestContext(request, {})
    return render_to_response("ticket_sales/test.html", vars)
