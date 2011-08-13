import re
from webob.exc import HTTPOk, HTTPMethodNotAllowed, HTTPNotFound

_notall = set(locals())
_notall.add('_notall')


class Router(object):
    def __init__(self):
        self.routes = []
        self._cls = None

    def __get__(self, obj, cls):
        bound = Router()
        bound.routes = self.routes
        bound._obj = obj
        bound._cls = cls
        return bound

    def add(self, regex, *methods):
        if not isinstance(regex, re._pattern_type):
            regex = re.compile(regex)
        if not methods:
            methods = ('GET', 'HEAD')
        def add(app):
            self.routes.append((regex, methods, app))
            return app
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

    def _handle_methods(self, allowed_methods, method):
        allowed_methods = ', '.join(allowed_methods)
        headers = [('Allow', allowed_methods)]
        if method == 'OPTIONS':
            return HTTPOk(
                explanation='The requested resource supports ',
                detail=allowed_methods,
                headers=headers,
            )
        return HTTPMethodNotAllowed(headers=headers)

    def dispatch(self, environ):
        path_info = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        allowed_methods = []
        for regex, methods, app in self.routes:
            m = regex.match(path_info)
            if m:
                if method not in methods:
                    allowed_methods.extend(methods)
                    continue
                self._update_environ(environ, m)
                if self._cls:
                    app = app.__get__(self._obj, self._cls)
                return app
        if allowed_methods:
            return self._handle_methods(allowed_methods, method)
        return HTTPNotFound()

    def __call__(self, environ, start_response):
        app = self.dispatch(environ)
        return app(environ, start_response)


__all__ = sorted(set(locals()) - _notall)
del _notall
