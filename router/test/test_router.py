import re
import unittest
from mock import Mock, sentinel, patch

from router import Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.environ = dict(
            SCRIPT_NAME='/foo',
            PATH_INFO='/bar/baz',
        )

    def test_dispatches_to_correct_app(self):
        self.router.add('/bar/baz$')(sentinel.app)
        self.assertIs(self.router.dispatch(self.environ), sentinel.app)

    def test_accepts_compiled_regexes(self):
        self.router.add(re.compile('/bar/baz$'))(sentinel.app)
        self.assertIs(self.router.dispatch(self.environ), sentinel.app)

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_routes(self, notfound):
        self.assertIs(
            self.router.dispatch(self.environ), notfound.return_value)
        notfound.assert_called_once_with()

    @patch('router.router.HTTPNotFound')
    def test_404_when_no_match(self, notfound):
        self.router.add('/bar/quux$')(sentinel.app)
        self.assertIs(
            self.router.dispatch(self.environ), notfound.return_value)
        notfound.assert_called_once_with()

    def test_call_calls_dispatched_app(self):
        with patch.object(
            self.router, 'dispatch', mocksignature=True
        ) as dispatch:
            body_iter = self.router(self.environ, sentinel.start_response)
            dispatch.assert_called_once_with(self.environ)
            dispatch.return_value.assert_called_once_with(
                self.environ, sentinel.start_response)

    def test_sets_script_name_and_path_info(self):
        self.router.add('/bar')(sentinel.app)
        self.router.dispatch(self.environ)
        self.assertEqual(self.environ['SCRIPT_NAME'], '/foo/bar')
        self.assertEqual(self.environ['PATH_INFO'], '/baz')

    def test_sets_wsgiorg_routing_args(self):
        self.router.add('/(b)a(?P<arrrg>r)')(sentinel.app)
        self.router.dispatch(self.environ)
        self.assertEqual(
            self.environ['wsgiorg.routing_args'], (('b', 'r'), {'arrrg': 'r'}))

    def test_updates_existing_wsgiorg_routing_args(self):
        self.environ['wsgiorg.routing_args'] = (
            ('arg1', 'arg2'),
            {'kw1': 'foo', 'arrrg': 'bar'},
        )
        self.router.add('/(b)a(?P<arrrg>r)')(sentinel.app)
        self.router.dispatch(self.environ)
        self.assertEqual(
            self.environ['wsgiorg.routing_args'],
            (
                ('arg1', 'arg2', 'b', 'r'),
                {'arrrg': 'r', 'kw1': 'foo'}
            )
        )

    try:
        _ = unittest.TestCase.assertIs
        del _
    except AttributeError:
        def assertIs(self, obj1, obj2):
            return self.assertTrue(obj1 is obj2)

if __name__ == '__main__':
    unittest.main()
