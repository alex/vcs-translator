from django.conf import settings
from django.conf.urls.defaults import patterns, include, url, handler404, handler500


urlpatterns = patterns("",
    url(r"", include("translator.urls")),
)

if settings.DEBUG:
    urlpatterns += patterns(
        url("^static/(?P<path>.*)$", "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT}),
    )
