import re
from webob.exc import HTTPOk, HTTPMethodNotAllowed, HTTPNotFound


class Router(object):
    def __init__(self):
        self.routes = []

    def add(self, regex):
        if not isinstance(regex, re._pattern_type):
            regex = re.compile(regex)
        def add(app):
            self.routes.append((regex, app))
        return add

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        for regex, app in self.routes:
            if regex.match(path):
                return app(environ, start_response)
        return HTTPNotFound()(environ, start_response)
