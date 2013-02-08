Middleware for WSGI-enabling Python callables including:

* Middleware that makes non-WSGI Python functions, callable classes, or methods into WSGI applications
* Middleware that automatically handles generating WSGI-compliant HTTP response codes, headers, and compliant iterators
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
