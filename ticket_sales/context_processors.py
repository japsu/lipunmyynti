def tracon_specific(request):
    from django.conf import settings
    return {"ANALYTICS_ACCOUNT": settings.ANALYTICS_ACCOUNT}
