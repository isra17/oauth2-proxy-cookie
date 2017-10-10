Support library to be used with [bitly/oauth2_proxy](https://github.com/bitly/oauth2_proxy)
to validate and decode the Cookie passed upstream. The library provide a Flask
extension to authorize requests based on the Cookie.

The reference implementation in Go is located [here](https://github.com/bitly/oauth2_proxy/blob/master/cookie/cookies.go).

Example:

.. code:: python

  from flask import request, abort
  from oauth2_proxy_cookie import Validator

  secret = <oauth2_proxy cookie secret>
  validator = Validator(secret, '_oauth2_proxy')
  cookie = request.headers.get('Cookie')
  value, time = validator.validate(cookie)

