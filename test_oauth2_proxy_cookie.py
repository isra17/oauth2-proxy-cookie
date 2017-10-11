import flask
import freezegun
import unittest
from datetime import datetime, timedelta
from oauth2_proxy_cookie import Validator, InvalidCookie, InvalidSignature, ExpiredCookie, OAuth2ProxyCookie

COOKIE_DATE = datetime(2017, 1, 1, 6, 0, 0)

EXPIRATION = timedelta(hours=1)
VALID_COOKIE = 'Zm9vQGJhcg==|1483250400|7_TbBXD14iv4kEh5wPWzTdTe0Oo='
INVALID_COOKIE = 'AAAA|1483250400|7_TbBXD14iv4kEh5wPWzTdTe0Oo='
EXPIRED_COOKIE = 'Zm9vQGJhcg==|1483254000|lCSWqvfyJY_QP8boDfT3mwEl3GI='


class OAuth2ProxyCookieTest(unittest.TestCase):
    def setUp(self):
        self.validator = Validator(
            b'ThisIsASecret', '_oauth2_proxy', timedelta(hours=1))

    @freezegun.freeze_time(COOKIE_DATE)
    def test_validate(self):
        self.assertEqual(
            self.validator.validate(VALID_COOKIE), (b'foo@bar', COOKIE_DATE))

        with self.assertRaises(InvalidCookie):
            self.validator.validate('foobar')

        with self.assertRaises(InvalidCookie):
            self.validator.validate('foobar|foo|asd|asd')

        with self.assertRaises(InvalidSignature):
            self.validator.validate(INVALID_COOKIE)

        with self.assertRaises(ExpiredCookie):
            self.validator.validate(EXPIRED_COOKIE)

class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask('test')
        self.app.testing = True
        self.client = self.app.test_client()
        @self.app.route('/')
        def index():
            return 'It works!'
        @self.app.route('/ping')
        def ping():
            return 'Pong'

    def test_extension(self):
        self.app.config.update({
            'OAUTH2_PROXY_COOKIE_SECRET': b'ThisIsASecret',
        })
        OAuth2ProxyCookie(allowed=['/ping']).init_app(self.app)

        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)

        rv = self.client.get('/', headers={'X-Forwarded-For': '1.1.1.1'})
        self.assertEqual(rv.status_code, 401)

        rv = self.client.get('/ping', headers={'X-Forwarded-For': '1.1.1.1'})
        self.assertEqual(rv.status_code, 200)

        self.client.set_cookie('localhost', '_oauth2_proxy', VALID_COOKIE)
        rv = self.client.get('/', headers={'X-Forwarded-For': '1.1.1.1'})
        self.assertEqual(rv.status_code, 200)
