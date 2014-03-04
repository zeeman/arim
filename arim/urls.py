from django.conf.urls import patterns, include, url

from .views import terms_view, device_view, devices_view, delete_device_view


urlpatterns = patterns('',
    url(r'^terms$', terms_view),
    url(r'^device$', device_view),
    url(r'^devices$', devices_view),
    url(r'^delete_device$', delete_device_view),
)
