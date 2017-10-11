import base64
import hashlib
import hmac
import six
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
        self.cookie_name = cookie_name.encode()
        self.expiration = expiration

    def validate(self, cookie_value):
        parts = cookie_value.split('|')
        if len(parts) != 3:
            raise InvalidCookie

        sig = self.sign(self.cookie_name, parts[0].encode(), parts[1].encode())
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
        h = hmac.new(self.secret, digestmod=hashlib.sha1)
        for arg in args:
            h.update(arg)
        return h.digest()

    def check_hmac(self, input_signature, signature):
        raw_input_signature = base64.urlsafe_b64decode(input_signature)
        return hmac.compare_digest(raw_input_signature, signature)
