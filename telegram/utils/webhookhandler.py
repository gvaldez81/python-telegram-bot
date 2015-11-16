import logging

from telegram import Update, NullHandler
from future.utils import bytes_to_native_str as n
import json
try:
    import BaseHTTPServer
except ImportError:
    import http.server as BaseHTTPServer


H = NullHandler()
logging.getLogger(__name__).addHandler(H)


class WebhookServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, update_queue,
                 webhook_path):
        super().__init__(server_address, RequestHandlerClass)
        self.update_queue = update_queue
        self.webhook_path = webhook_path


# WebhookHandler, process webhook calls
# Based on: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/
# examples/webhook_examples/webhook_cpython_echo_bot.py
class WebhookHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "WebhookHandler/1.0"

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.logger = logging.getLogger(__name__)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == self.server.webhook_path and \
           'content-type' in self.headers and \
           'content-length' in self.headers and \
           self.headers['content-type'] == 'application/json':
            json_string = \
                n(self.rfile.read(int(self.headers['content-length'])))

            self.send_response(200)
            self.end_headers()

            update = Update.de_json(json.loads(json_string))
            self.server.update_queue.put(update)

        else:
            self.send_error(403)
            self.end_headers()