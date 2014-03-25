import json
import urllib
import urllib2
from time import sleep
from django.conf import settings
from sys import stderr

from arim.settings import DEBUG


class Conrad(object):
    """
    Basic class for getting data from the Cyder API. This should work with API
    v1, but compatibility is not guaranteed.
    """
    def __init__(self, token, base_url):
        """
        Params:
          - token       The API token to authenticate with.
          - base_url    The url to prepend to each request. Use a consistent
                        scheme of trailing or leading slashes.
        """
        self.token = token
        self.base_url = base_url
        self.result_str = None  # holds the last result as a string
        self.result = None  # if result_str contains a valid JSON object,
                            # this contains a deserialized representation of
                            # that object
        self.num_results = None
        self.response_code = None  # holds the last request's response code
        self.exception = None  # contains last exception raised
        self.prev_url = None
        self.next_url = None

    def get(self, path, pk=None, query=None, verbatim=False):
        """
        Params:
        path    The specific path to access under self.base_url. May or
                may not need a leading slash depending on the value of
                base_url.
        query   A dict or string of GET parameters.
        verbatim    Whether or not to treat path as the entire URL.

        Returns the deserialized output of the API if successful or False if
        unsuccessful.
        """

        if query:
            if isinstance(query, dict):
                query = urllib.urlencode(query)

            query = "count=100&" + query
        else:
            query = "count=100"

        url = self.build_url(path, extra=pk, query=query, verbatim=verbatim)

        req = urllib2.Request(url)
        req.add_header('Authorization', 'Token ' + self.token)

        resp = self.do_request(req)

        self.result_str = resp.read()
        self.response_code = resp.code

        result = json.loads(self.result_str)

        self.result = result.get('results', None)

        if self.result is None:
            self.result = result

        self.prev_url = result.get('previous', None)
        self.next_url = result.get('next', None)
        self.num_results = long(result.get('count', 1))

        sleep(0.1)  # sleep to avoid overwhelming the server
        return self.result

    def get_next(self):
        if self.next_url is None:
            return False
        return self.get(self.next_url, verbatim=True)

    def get_prev(self):
        if self.prev_url is None:
            return False
        return self.get(self.prev_url, verbatim=True)

    def post(self, path, data, extra=False, verbatim=False, method=None):
        """
        path - The path to access. If verbatim is false, it is appended to
               self.base_url, otherwise it is sent raw.
        data - A dict containing the data to send or a JSON string.
        extra - Data to append to the path.
        verbatim - If False, self.base_url is prepended to path.
        method - Used to set an alternate method if needed.
        """
        url = self.build_url(path, extra=extra, verbatim=verbatim)

        if isinstance(data, dict):
            request_data = json.dumps(data)
        else:
            request_data = data

        request = urllib2.Request(url, request_data)
        request.add_header('Authorization', 'Token ' + self.token)
        request.add_header('Content-Type', 'application/json')

        # handle non-POST requests
        if method:
            request.get_method = lambda: method.upper()
        response = self.do_request(request)
        content = json.loads(response.read())
        return content

    def put(self, path, pk, data, verbatim=False):
        return self.post(path, data, extra=pk, verbatim=verbatim, method="PUT")

    def patch(self, path, pk, data, verbatim=False):
        return self.post(path, data, extra=pk, verbatim=verbatim,
                         method="PATCH")

    def delete(self, path, pk, verbatim=False):
        url = self.build_url(path, pk, verbatim)

        request = urllib2.Request(url)
        request.add_header('Authorization', 'Token ' + self.token)
        # request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: "DELETE"

        response = self.do_request(request)
        content = response.read()
        return content

    def build_url(self, path, extra=None, query=None, verbatim=False):
        url = ""
        if not verbatim:
            url += self.base_url
        url += path

        if url[-1] != "/":
            url += "/"

        if extra:
            url += str(extra)

        if url[-1] != "/":
            url += "/"

        if query:
            if query[0] != "?":
                url += "?"
            url += query

        return url

    def do_request(self, request):
        if DEBUG:
            try:
                return urllib2.urlopen(request)
            except urllib2.HTTPError as e:
                stderr.write(u"API request failed\n")
                stderr.write(u'    ' + request.get_full_url() + u'\n')
                stderr.write(u'    ' + request.get_data() + u'\n')
                stderr.write(u''.join(u'    ' + line + u'\n'
                                      for line in e.fp.read().splitlines()))
                raise
        else:
            return urllib2.urlopen(request)
