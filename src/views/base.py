import json
import logging
import websocket
import tornado.web
from tornado.template import Loader


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.websocket = websocket.WebSocket(sslopt={'cert_reqs': 0})

    def response(self, data):
        format = self.get_argument('format', default=None)
        if isinstance(data, (dict, list, tuple)):
            format = json

        if format == 'json':
            data = json.dumps({'data': data})

        logging.info('Response: %s' % data)
        self.write(data)

    def render(self, template, **kwargs):
        loader = Loader('templates')
        self.write(loader.load(template).generate(**kwargs))