from django.conf.urls import patterns, include, url

from .views import terms, devices


urlpatterns = patterns('',
    url(r'^terms$', terms),
    url(r'^devices$', devices),
)
