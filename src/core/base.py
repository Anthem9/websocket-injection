import json
import uuid
import logging
import thread
import websocket
import tornado.web
import tornado.gen
from tornado.template import Loader


class Client(dict):

    def __init__(self, uuid):
        super(Client, self).__init__()
        self.uuid = uuid
        self.has_send = False
        self.is_params = False
        self.message = []

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        return '<Client: %s(%s)>' % (self.uuid, str(self.has_send))


class WebSocketAppMixin(object):
    url = None
    client = None
    clients = list()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebSocketAppMixin, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def on_message(self, websocket, message):
        logging.info('Recv: %s' % message)
        self.response(message)

    def on_close(self, websocket):
        logging.critical('Connection closed')
        self.client.ws = None

    def run_websocket(self, url):
        if not self.client.ws:
            self.client.ws = websocket.WebSocketApp(url=url, on_message=self.on_message)
            thread.start_new(self.client.ws.run_forever, ())

    def add_client(self, uuid):
        self.clients.append(Client(uuid=uuid))

    def get_client(self, uuid):
        client = next((l for l in self.clients if l.uuid == uuid), None)
        if not client:
            client = Client(uuid=uuid)
            self.clients.append(client)
        return client


class BaseHandler(tornado.web.RequestHandler, WebSocketAppMixin):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        session_id = self.get_secure_cookie('uuid')
        if not session_id:
            session_id = str(uuid.uuid1())
            self.set_secure_cookie('uuid', session_id)
        self.client = self.get_client(session_id)
        self.client.has_send = False

    def response(self, data):
        format = self.get_argument('format', default=None)

        if not self.client.has_send:
            logging.info('Response: %s' % data)
            self.client.has_send = True
            self.client.message.append(data)
            if format == 'json':
                response = json.dumps(self.client.message)
            else:
                response = ''.join(self.client.message)
            self.write(response)
            self.client.message = []
            self.finish()

            if self.client.is_params:
                self.client.ws.close()
                self.client.ws = None

        else:
            self.client.message.append(data)
            self.client.has_send = False

    def render(self, template, **kwargs):
        loader = Loader('templates')
        self.write(loader.load(template).generate(**kwargs))
        self.finish()