from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import logging
from threading import Thread
import json
from datetime import datetime


BASE_DIR = pathlib.Path()
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
FOR_SAVE = {}


def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        result = {str(datetime.now()): data_dict}
        FOR_SAVE.update(result)
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(FOR_SAVE, fd, ensure_ascii=False, indent=2)
    except ValueError as a:
        logging.error(f"ValueError in save_data: {a}")
    except OSError as b:
        logging.error(f"OSError in save_data: {b}")


def send_to_socket(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, (SERVER_IP, SERVER_PORT))
    client_socket.close()


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path)
        if url_path.path == '/':
            self.send_html_file('index.html')
        elif url_path.path == '/contact':
            self.send_html_file('contact.html')
        else:
            if pathlib.Path().joinpath(url_path.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_web(server_class=HTTPServer, http_handler=HttpHandler):
    address = ("", 3000)
    http = server_class(address, http_handler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_socket(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    server_socket.bind(server)
    try:
        while True:
            data, address = server_socket.recvfrom(1024)
            save_data(data)
    except KeyboardInterrupt:
        logging.info("Socket server stopped")
    finally:
        server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")
    th_web = Thread(target=run_web)
    th_web.start()

    th_socket = Thread(target=run_socket(SERVER_IP, SERVER_PORT))
    th_socket.start()
