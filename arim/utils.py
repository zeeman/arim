from django.http import HttpResponse


class HttpResponse422(HttpResponse):
    status_code = 422
