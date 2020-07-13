import base64
import hashlib
import hmac
import six
import logging
from datetime import datetime, timedelta


class ValidateError(Exception):
    pass


class InvalidCookie(ValidateError):
    pass


class InvalidSignature(ValidateError):
    pass


class ExpiredCookie(ValidateError):
    pass


class Validator(object):
    def __init__(self, secret, cookie_name, expiration=timedelta(days=7)):
        if not cookie_name or not isinstance(cookie_name, str):
            raise ValueError('cookie_name must be str')

        if not secret or not isinstance(secret, six.binary_type):
            raise ValueError('secret must be non-empty bytes')

        if not isinstance(expiration, timedelta):
            raise ValueError('expiration must be datetime.timedelta')

        self.secret = secret
        self.cookie_name = cookie_name
        self.expiration = expiration

    def validate(self, cookie_value):
        if six.PY2 and isinstance(cookie_value, unicode):
            cookie_value = cookie_value.encode()

        if not cookie_value:
            raise InvalidCookie

        parts = cookie_value.split('|')
        if len(parts) != 3:
            raise InvalidCookie

        sig = self.sign(self.cookie_name, parts[0], parts[1])
        if not self.check_hmac(parts[2], sig):
            raise InvalidSignature

        cookie_date = datetime.utcfromtimestamp(int(parts[1]))
        now = datetime.utcnow()
        if cookie_date < (now - self.expiration) \
                or cookie_date > (now + timedelta(minutes=5)):
            raise ExpiredCookie

        value = base64.urlsafe_b64decode(parts[0])
        return value, cookie_date

    def sign(self, *args):
        h = hmac.new(self.secret, digestmod=hashlib.sha256)
        for arg in args:
            h.update(arg.encode())
        return h.digest()

    def check_hmac(self, input_signature, signature):
        raw_input_signature = base64.urlsafe_b64decode(input_signature)
        return hmac.compare_digest(raw_input_signature, signature)


class OAuth2ProxyCookie(object):
    def __init__(self, app=None, force_https=True, allowed=None):
        self.force_https = force_https
        self.allowed = allowed or []
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.validator = Validator(
            secret=app.config.get('OAUTH2_PROXY_COOKIE_SECRET'),
            cookie_name=app.config.get('OAUTH2_PROXY_COOKIE_NAME',
                                       '_oauth2_proxy'),
            expiration=app.config.get(
                'OAUTH2_PROXY_COOKIE_EXPIRATION', timedelta(days=7)))

        app.before_request(self.check_auth)

    def check_auth(self):
        from flask import request, abort, g
        # Internal query are not authenticated.
        if not request.headers.get('x-forwarded-for', None):
            return

        # HTTPS from the outside.
        if self.force_https and request.headers.get('x-forwarded-proto',
                                                    None) == 'http':
            return redirect(request.url.replace('http://', 'https://'))

        # Allowed public endpoints.
        if request.url_rule:
            for allowed in self.allowed:
                if allowed == request.url_rule.rule:
                    return

        cookie = request.cookies.get(self.validator.cookie_name)
        try:
            user_id, _ = self.validator.validate(cookie)
        except ValidateError as e:
            self.logger.error('Invalid OAuth2Proxy cookie: {} | {}'.format(
                cookie, e.__class__.__name__))
            abort(401)

        g.user = user_id.decode()
