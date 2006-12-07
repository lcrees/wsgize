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

'''Utilities for "WSGIzing" Python callables including:

    * An WSGI-compliant HTTP response generator
    * A decorator for making non-WSGI Python callables (functions, classes classes overriding __call__) into WSGI callables
    * A secondary WSGI dispatcher.
    * A decorator for autogenerating WSGI start_response response codes and headers and compliant iterators for WSGI callables
'''

import sys
from BaseHTTPServer import BaseHTTPRequestHandler as _bhrh

thing = set('Allow', 'Content-Encoding', 'Content-Language', 'Content-Length', 'Content-Location', 'Content-MD5',
 'Content-Range', 'Content-Type', 'Expires', 'Last-Modified', 'Cache-Control', 'Connection', 'Date', 'Pragma',
 'Trailer', 'Transfer-Encoding', 'Upgrade', 'Via', 'Warning', 'Accept-Ranges', 'Age', 'ETag', 'Location',
 'Proxy-Authenticate', 'Retry-After', 'Server', 'Vary', 'WWW-Authenticate')
 
 

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

def response(code):
    '''Returns a WSGI response string.

    code HTTP response (integer)
    '''
    return '%i %s' % (code, _bhrh.responses[code][0])       

    
class Wsgize(object):

    '''Autogenerates WSGI start_response callables, headers, and iterators for
    a WSGI callables.
    '''    

    def __init__(self, app, **kw):
        '''@param application WSGI callable
        @param kw Keyword arguments
        '''
        self.application = app
        # Get HTTP response
        self.start_response = response(kw.get('response', 200))
        # Generate headers
        exheaders = kw.get('headers', dict())
        headers = list((key, exheaders[key]) for key in exheaders)
        self.headers = [('Content-type', kw.get('mime', 'text/html'))] + headers
        self.exc_info = kw.get('exc_info', None)
        # Key for kwargs passed through environ dictionary
        self.kwargkey = kw.get('kwargs', 'wsgize.kwargs')
        # Key for kargs passed through environ dictionary
        self.argkey = kw.get('args', 'wsgize.args')

    def __call__(self, environ, start_response):
        '''Passes WSGI params to a callable and autogenrates the start_response.'''
        data = self.application(environ, start_response)
        start_response(self.start_response, self.headers, self.exc_info)
        if hasattr(data, '__iter__'):
            # Wrap strings in non-string iterator
            if isinstance(data, basestring): data = [data]
            return data
        else:
            raise TypeError('Data returned by callable must be iterable or string.')        


class WsgiWrap(Wsgize):

    '''Makes arbitrary Python callables WSGI callables.'''     

    def __call__(self, environ, start_response):
        '''Makes a Python callable a WSGI callable.'''
        # Get any arguments
        args = environ.get(self.argkey, False)
        # Get any keyword arguments
        kw = environ.get(self.kwargkey, False)
        # Pass args/kwargs to non-WSGI callable
        if args and kw:
            data = self.application(*args, **kw)
        elif args:
            data = self.application(*args)
        elif kw:
            data = self.application(**kw)
        start_response(self.start_response, self.headers, self.exc_info)
        if isinstance(data, basestring): data = [data]
        return data


class WsgiRoute(object):

    '''Secondary WSGI dispatcher.'''

    def __init__(self, *args, **kw):
        '''@param table Dictionary of names and callables.'''
        self.table, self.modpath = args[0], kw.get('modpath', '')
        # Get key for callable
        self.kwargkey = kw.get('kwargkey', 'wsgize.callable')
        syspaths = kw.get('syspaths', None)
        # Add any additional sys paths
        if syspaths is not None:
            for path in syspaths: sys.path.append(path)

    def __call__(self, environ, start_response):
        '''Passes WSGI params to a callable based on a keyword.'''
        callback = self.lookup(environ[self.kwargkey])
        return callback(environ, start_response)           

    def get_mod_func(self, callback):
        '''Breaks a callable name out from a module name.

        @param callback Name of a callback        
        '''
        # Add shortcut to module if present
        if self.modpath != '': callback = '.'.join([self.modpath, callback])
        dot = callback.rindex('.')
        return callback[:dot], callback[dot+1:]

    def lookup(self, kw):
        '''Fetches a callable based on keyword.

        kw Keyword
        '''
        callable = self.table[kw]
        if not isinstance(callable, basestring):
            return callable
        else:
            return self.get_callback(callable)
        raise ImportError()    

    def get_callback(self, callback):
        '''Loads a callable from system path.

        callback A callback's name'''        
        mod_name, func_name = self.get_mod_func(callback)
        try:
            return getattr(__import__(mod_name, '', '', ['']), func_name)
        except ImportError, error:
            raise ImportError(
                'Could not import %s. Error was: %s' % (mod_name, str(error)))
        except AttributeError, error:
            raise AttributeError(
                'Tried %s in module %s. Error was: %s' % (func_name,
                 mod_name, str(error)))


__all__ = ['response', 'Wsgize', 'WsgiWrap', 'WsgiRoute', 'wsgize', 'wsgiwrap']