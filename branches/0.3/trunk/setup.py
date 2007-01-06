# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''setup - setuptools based setup for wsgize.'''

import ez_setup
ez_setup.use_setuptools()

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='wsgize',
      version='0.4',
      description='''WSGI without the WSGI''',
      long_description=''''Middleware for WSGI-enabling Python callables
including:

* Middleware that makes non-WSGI Python functions, callable classes, or
methods into WSGI applications
* Middleware that automatically handles generating WSGI-compliant HTTP
response codes, headers, and compliant iterators
* An HTTP response generator
* A secondary WSGI dispatcher

Examples:

# Automatically handle HTTP response, header, and iterator generation

@wsgize()
def app(environ, start_response):
    return 'Hello World'

# Make a normal Python function into a WSGI application

@wsgiwrap()
def app(name):
    return 'Hello ' % name
''',
      author='L. C. Rees',
      author_email='lcrees@gmail.com',
      license='BSD',
      packages = ['wsgize'],
      zip_safe = True,
      keywords='WSGI dispatch middleware web HTTP decorators',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers', 
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Internet :: WWW/HTTP :: WSGI',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware'])