from django.conf.urls import patterns, include, url

from .views import index, terms, devices


urlpatterns = patterns('',
    url(r'^$', index),
    url(r'^terms$', terms),
    url(r'^devices$', devices),
)
