from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='oauth2-proxy-cookie',

    version='0.1.0',

    description='''bitly/oauth2-proxy compatible library to decode and validate
                authenticated cookie.''',
    long_description=long_description,

    url='https://github.com/isra17/oauth2-proxy-cookie',

    author='isra17',
    author_email='isra017@gmail.com',

    license='LGPLv3+',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers'
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='oauth2-proxy authentication',

    py_modules=['oauth2_proxy_cookie'],

    install_requires=['six'],
)
