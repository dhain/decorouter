import re
import unittest
from mock import Mock, sentinel, patch

from decorouter import Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.environ = dict(
            SCRIPT_NAME='/foo',
            PATH_INFO='/bar/baz',
            REQUEST_METHOD='GET',
        )

    def test_add_returns_added_app(self):
        self.assertIs(self.router.add('')(sentinel.app), sentinel.app)

    def test_dispatches_to_correct_app(self):
        self.router.add('/bar/baz$')(sentinel.app)
        self.assertIs(self.router.dispatch(self.environ), sentinel.app)

    def test_accepts_compiled_regexes(self):
        self.router.add(re.compile('/bar/baz$'))(sentinel.app)
        self.assertIs(self.router.dispatch(self.environ), sentinel.app)

    @patch('decorouter.router.HTTPNotFound')
    def test_404_when_no_routes(self, notfound):
        self.assertIs(
            self.router.dispatch(self.environ), notfound.return_value)
        notfound.assert_called_once_with()

    @patch('decorouter.router.HTTPNotFound')
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

    @patch('decorouter.router.HTTPMethodNotAllowed')
    def test_method_not_allowed(self, notallowed):
        self.router.add('/bar/baz$', 'POST')(sentinel.app)
        self.assertIs(
            self.router.dispatch(self.environ), notallowed.return_value)
        notallowed.assert_called_once_with(
            headers=[('Allow', 'POST')])

    @patch('decorouter.router.HTTPMethodNotAllowed')
    def test_method_allowed_by_later_match(self, notallowed):
        self.router.add('/bar/baz$', 'POST')(sentinel.post_app)
        self.router.add('/bar/baz$')(sentinel.app)
        self.assertIs(self.router.dispatch(self.environ), sentinel.app)

    @patch('decorouter.router.HTTPMethodNotAllowed')
    def test_method_not_allowed_multiple_matches(self, notallowed):
        self.router.add('/bar/baz$', 'POST', 'UPDATE')(sentinel.post_app)
        self.router.add('/bar/baz$', 'DELETE')(sentinel.delete_app)
        self.assertIs(
            self.router.dispatch(self.environ), notallowed.return_value)
        notallowed.assert_called_once_with(
            headers=[('Allow', 'POST, UPDATE, DELETE')])

    @patch('decorouter.router.HTTPOk')
    def test_options(self, ok):
        self.router.add('/bar/baz$', 'POST', 'UPDATE')(sentinel.post_app)
        self.router.add('/bar/baz$', 'DELETE')(sentinel.delete_app)
        self.environ['REQUEST_METHOD'] = 'OPTIONS'
        self.assertIs(self.router.dispatch(self.environ), ok.return_value)
        methods = 'POST, UPDATE, DELETE'
        ok.assert_called_once_with(
            explanation='The requested resource supports ',
            detail=methods,
            headers=[('Allow', methods)],
        )

    def test_binds_methods(self):
        class MyClass:
            router = self.router
            @router.add('/bar/baz$')
            def baz(self):
                pass
        instance = MyClass()
        app = instance.router.dispatch(self.environ)
        self.assertIs(app.im_self, instance)
        self.assertIs(app.im_func, MyClass.baz.im_func)

    try:
        _ = unittest.TestCase.assertIs
        del _
    except AttributeError:
        def assertIs(self, obj1, obj2):
            return self.assertTrue(obj1 is obj2, '%r is not %r' % (obj1, obj2))

if __name__ == '__main__':
    unittest.main()
