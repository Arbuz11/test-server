from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/stats':
            self._set_headers()
            self.wfile.write("You requested statistics".encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write("File not found".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        if not post_data:
            self._set_headers(400)  # Bad request - No data
            self.wfile.write("Bad request: No data provided".encode('utf-8'))
            return

        # Проверка на число
        try:
            number = float(post_data)

            # Пример дополнительных проверок
            if number < 0:
                self._set_headers(403)  # Forbidden
                self.wfile.write("Forbidden: Negative numbers are not allowed.".encode('utf-8'))
            elif number == 0:
                self._set_headers(204)  # No Content
                self.wfile.write(b"")  # No content
            elif number > 1000:
                self._set_headers(413)  # Request Entity Too Large
                self.wfile.write("Request Entity Too Large: Number exceeds limit.".encode('utf-8'))
            else:
                self._set_headers(200)  # OK
                self.wfile.write("Data passed validation and is acceptable.".encode('utf-8'))

        except ValueError:
            self._set_headers(422)  # Unprocessable Entity
            self.wfile.write("Unprocessable Entity: Not a valid number.".encode('utf-8'))
            return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

def serve_forever(server):
    server.serve_forever()

if __name__ == "__main__":
    server = ThreadedHTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    print("Server started on localhost:8000")

    try:
        server_thread = threading.Thread(target=serve_forever, args=(server,))
        server_thread.daemon = True
        server_thread.start()
        server_thread.join()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()