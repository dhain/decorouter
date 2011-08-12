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

    def dispatch(self, path_info):
        for regex, app in self.routes:
            if regex.match(path_info):
                return app
        return HTTPNotFound()

    def __call__(self, environ, start_response):
        app = self.dispatch(environ['PATH_INFO'])
        return app(environ, start_response)
