============
 Decorouter
============

Decorouter is a WSGI routing apparatus that makes it easy to define routes
using decorator syntax.

Example::

    from decorouter import Router

    class MyApplication:
        router = Router()

        @router.add('/$')
        def index(self, environ, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['Hello, world!']

        @router.add('/hello/([^/]+)$')
        def index(self, environ, start_response):
            args, kwargs = environ['wsgiorg.routing_args']
            (name,) = args
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['Hello, %s!' % (name,)]

        def __call__(self, environ, start_response):
            return self.router(environ, start_response)

    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, MyApplication()).serve_forever()
