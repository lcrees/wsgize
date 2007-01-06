# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Middleware for WSGI-enabling Python callables including:

* An WSGI-compliant HTTP response generator
* A wrapper and decorator for making non-WSGI Python functions, callable
classes or methods into WSGI callables
* A secondary WSGI dispatcher.
* A decorator for autogenerating HTTP response codes, headers, and
  compliant iterators for WSGI callables
'''

__author__ = 'L.C. Rees (lcrees-at-gmail.com)'
__revision__ = '0.4'

import sys
from BaseHTTPServer import BaseHTTPRequestHandler as _bhrh

__all__ = ['response', 'Wsgize', 'WsgiWrap', 'WsgiRoute', 'wsgize',
    'wsgiwrap', 'route', 'register']

# Secondary dispatcher routing table
routes = dict()

def register(name, application):
    '''Registers a mapping of a name to an WSGI application.

    @param pattern URL pattern
    @param application WSGI application
    '''
    routes[name] = application

def response(code):
    '''Returns a WSGI response string.

    code HTTP response (integer)
    '''
    return '%i %s' % (code, _bhrh.responses[code][0])

def route(name):
    '''Callable decorator for an application with the secondary dispatcher.'''
    def decorator(application):
        register(name, application)
        return application
    return decorator

def wsgize(**kw):
    '''Decorator for Wsgize.

    @param application Application to decorate.
    '''
    def decorator(application):
        return Wsgize(application, **kw)
    return decorator

def wsgiwrap(**kw):
    '''Decorator for WsgiWrap.

    @param application Application to decorate.
    '''    
    def decorator(application):
        return WsgiWrap(application, **kw)
    return decorator     

    
class Wsgize(object):

    '''Autogenerates WSGI start_response callables, headers, and iterators for
    a WSGI application.
    '''    

    def __init__(self, app, **kw):
        self.application = app
        # Get HTTP response
        self.response = response(kw.get('response', 200))
        # Generate headers
        exheaders = kw.get('headers', dict())
        headers = list((key, exheaders[key]) for key in exheaders)
        self.headers = [('Content-type', kw.get('mime', 'text/html'))] + headers
        self.exc_info = kw.get('exc_info', None)
        # Key for kwargs passed through environ dictionary
        self.kwargkey = kw.get('kwargs', 'wsgize.kwargs')
        # Key for kargs passed through environ dictionary
        self.argkey = kw.get('args', 'wsgize.args')
        # Single URL vars key
        self.key = kw.get('routing_args', 'wsgiorg.routing_args')

    def __call__(self, environ, start_response):
        '''Passes WSGI params to a callable and autogenrates the start_response.'''
        data = self.application(environ, start_response)
        start_response(self.response, self.headers, self.exc_info)
        # Wrap strings in non-string iterator, ensuring its a normal ASCII string
        if isinstance(data, basestring): data = [str(data)]
        if hasattr(data, '__iter__'): return data
        raise TypeError('Data returned by callable must be iterable.')        


class WsgiWrap(Wsgize):

    '''Makes arbitrary Python callables WSGI applications.'''     

    def __call__(self, environ, start_response):
        '''Makes a Python callable a WSGI callable.'''
        # Try unified WSGI URL vars keyword
        try:
            args, kw = environ.get(self.key)
        except ValueError:
            # Get any arguments
            args = environ.get(self.argkey, ())
            # Get any keyword arguments
            kw = environ.get(self.kwargkey, {})
        # Pass args/kwargs to non-WSGI callable
        if args and kw:
            data = self.application(*args, **kw)
        elif args:
            data = self.application(*args)
        elif kw:
            data = self.application(**kw)        
        start_response(self.response, self.headers, self.exc_info)
        # Wrap strings in non-string iterator, ensuring its a normal ASCII string
        if isinstance(data, basestring): data = [str(data)]
        if hasattr(data, '__iter__'): return data
        raise TypeError('Data returned by callable must be iterable.')


class WsgiRoute(object):

    '''Secondary WSGI dispatcher.'''

    def __init__(self, table=None, **kw):
        '''@param table Dictionary of names and callables.'''
        # Secondary dispatcher routing table
        if table is not None:
            self.table = table
        # Use external routing table
        else:
            self.table = routes
        # Default module path
        self.modpath = kw.get('modpath', '')
        # Get key for callable
        self.key = kw.get('key', 'wsgize.callable')

    def __call__(self, environ, start_response):
        '''Passes WSGI params to a callable based on a keyword.'''
        callback = self.lookup(environ[self.key])
        return callback(environ, start_response)

    def getapp(self, app):
        '''Loads a callable based on its name

        @param app An WSGI application's name'''
        # Add shortcut to module if present
        if self.modpath != '': app = '.'.join([self.modpath, app])
        dot = app.rindex('.')
        # Import module
        return getattr(__import__(app[:dot], '', '', ['']), app[dot+1:])

    def lookup(self, kw):
        '''Fetches an application based on keyword.

        @param kw Keyword
        '''
        callback = self.table[kw]
        if hasattr(callback, '__call__'):
            return callback
        else:
            return self.getapp(callback)