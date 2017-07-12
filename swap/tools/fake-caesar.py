
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import wraps

def debug(func):
    @wraps(func)
    def wrapper(self):
        print(self.requestline, self.headers)

        length = int(self.headers.get('content-length'))
        print(self.rfile.read(length))
        return func(self)
    return wrapper

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        request_path = self.path

        print("\n----- Request Start ----->\n")
        print(request_path)
        print(self.headers)
        print("<----- Request End -----\n")

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        request_path = self.path

        print("\n----- Request Start ----->\n")
        print(request_path)

        request_headers = self.headers
        content_length = request_headers.get('content-length')
        length = int(content_length) if content_length else 0

        print(request_headers)
        print(self.rfile.read(length))
        print("<----- Request End -----\n")

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    do_PUT = do_POST
    do_DELETE = do_GET

httpd = HTTPServer(('localhost', 3000), Handler)
httpd.serve_forever()
