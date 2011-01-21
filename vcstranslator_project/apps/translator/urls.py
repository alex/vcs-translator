from django.conf.urls.defaults import patterns, include, url, handler404, handler500


urlpatterns = patterns("translator.views",
    url(r"^$", "home", name="home"),
    url(r"^feedback/$", "feedback", name="translation_feedback"),
)
