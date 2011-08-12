import re
import unittest
from mock import Mock, sentinel, patch

from router import Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()

    def test_dispatches_to_correct_app(self):
        self.router.add('/$')(sentinel.app)
        self.assertIs(self.router.dispatch('/'), sentinel.app)

    def test_accepts_compiled_regexes(self):
        self.router.add(re.compile('/$'))(sentinel.app)
        self.assertIs(self.router.dispatch('/'), sentinel.app)

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_routes(self, notfound):
        self.assertIs(self.router.dispatch('/'), notfound.return_value)
        notfound.assert_called_once_with()

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_match(self, notfound):
        self.router.add('/$')(sentinel.app)
        self.assertIs(self.router.dispatch('/foo'), notfound.return_value)
        notfound.assert_called_once_with()

    def test_call_calls_dispatched_app(self):
        environ = dict(
            PATH_INFO='/',
        )
        with patch.object(
            self.router, 'dispatch', mocksignature=True
        ) as dispatch:
            body_iter = self.router(environ, sentinel.start_response)
            dispatch.assert_called_once_with(environ['PATH_INFO'])
            dispatch.return_value.assert_called_once_with(
                environ, sentinel.start_response)

    try:
        _ = unittest.TestCase.assertIs
        del _
    except AttributeError:
        def assertIs(self, obj1, obj2):
            return self.assertTrue(obj1 is obj2)

if __name__ == '__main__':
    unittest.main()
