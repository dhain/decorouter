import re
import unittest
from mock import Mock, sentinel, patch

from router import Router


class TestRouter(unittest.TestCase):
    def test_dispatches_wsgi_request(self):
        app = Mock()
        router = Router()
        router.add('/$')(app)
        environ = dict(
            PATH_INFO='/',
        )
        body_iter = router(environ, sentinel.start_response)
        app.assert_called_once_with(environ, sentinel.start_response)
        self.assertIs(body_iter, app.return_value)

    def test_accepts_compiled_regexes(self):
        app = Mock()
        router = Router()
        router.add(re.compile('/$'))(app)
        environ = dict(
            PATH_INFO='/',
        )
        body_iter = router(environ, sentinel.start_response)
        app.assert_called_once_with(environ, sentinel.start_response)
        self.assertIs(body_iter, app.return_value)

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_routes(self, notfound):
        notfound.return_value = Mock()
        router = Router()
        environ = dict(
            PATH_INFO='/foo',
        )
        body_iter = router(environ, sentinel.start_response)
        notfound.assert_called_once_with()
        notfound.return_value.assert_called_once_with(
            environ, sentinel.start_response)
        self.assertIs(body_iter, notfound.return_value.return_value)

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_match(self, notfound):
        notfound.return_value = Mock()
        app = Mock()
        router = Router()
        router.add('/$')(app)
        environ = dict(
            PATH_INFO='/foo',
        )
        body_iter = router(environ, sentinel.start_response)
        self.assertFalse(app.called)
        notfound.assert_called_once_with()
        notfound.return_value.assert_called_once_with(
            environ, sentinel.start_response)
        self.assertIs(body_iter, notfound.return_value.return_value)

    try:
        _ = unittest.TestCase.assertIs
        del _
    except AttributeError:
        def assertIs(self, obj1, obj2):
            return self.assertTrue(obj1 is obj2)

if __name__ == '__main__':
    unittest.main()
