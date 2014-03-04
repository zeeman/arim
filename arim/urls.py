from django.conf.urls import patterns, include, url

from .views import terms, device, devices


urlpatterns = patterns('',
    url(r'^terms$', terms),
    url(r'^device$', device),
    url(r'^devices$', devices),
)
