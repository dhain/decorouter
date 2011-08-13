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

    def _update_environ(self, environ, m):
        environ['SCRIPT_NAME'] += m.group(0)
        environ['PATH_INFO'] = environ['PATH_INFO'][m.end():]
        old_args, old_kws = environ.get(
            'wsgiorg.routing_args', ((), {}))
        environ['wsgiorg.routing_args'] = (
            tuple(old_args) + m.groups(),
            dict(old_kws, **m.groupdict())
        )

    def dispatch(self, environ):
        path_info = environ['PATH_INFO']
        for regex, app in self.routes:
            m = regex.match(path_info)
            if m:
                self._update_environ(environ, m)
                return app
        return HTTPNotFound()

    def __call__(self, environ, start_response):
        app = self.dispatch(environ)
        return app(environ, start_response)
