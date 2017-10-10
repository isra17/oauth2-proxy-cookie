Support library to be used with [bitly/oauth2_proxy](https://github.com/bitly/oauth2_proxy)
to validate and decode the Cookie passed upstream. The library provide a Flask
extension to authorize requests based on the Cookie.

The reference implementation in Go is located [here](https://github.com/bitly/oauth2_proxy/blob/master/cookie/cookies.go).

Example:

.. code:: python

  from flask import request, abort
  from oauth2_proxy_cookie import validate, InvalidSignature

  secret = <oauth2_proxy cookie secret>
  cookie = request.headers.get('Cookie')
  try:
    value, time = validate(cookie)
  except InvalidSignature as e:
    abort(401)



