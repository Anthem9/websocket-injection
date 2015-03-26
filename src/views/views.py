import logging
from requests.models import RequestEncodingMixin
from tornado.escape import parse_qs_bytes
from tornado.web import asynchronous
from core.base import BaseHandler
from core.exceptions import UnexpectedReuqestDataException, InvalidWebSocketURLException


class SQLMapHandler(BaseHandler):
    def get(self):
        self.post()

    @asynchronous
    def post(self):
        url = self.get_argument('url', default=None)
        data = self.get_argument('data', default=None)
        self.client.is_params = self.get_argument('is_params', default=False)
        # `query_str` is the query string of websocket
        query_str = RequestEncodingMixin._encode_params(parse_qs_bytes(self.request.body))
        if not url or (not data and not query_str):
            raise UnexpectedReuqestDataException

        if not url.startswith('ws://') and not url.startswith('wss://'):
            raise InvalidWebSocketURLException

        if query_str:
            logging.info('Request query string: %s' % query_str)
        if data:
            logging.info('Request message: %s' % data)

        if not self.client.ws:
            self.run_websocket('%s?%s' % (url, query_str))
        else:
            self.client.has_send = False
            self.client.ws.send(data if data else '')

    def get_argument(self, name, default=None, strip=True):
        return self._get_argument(name, default=default,
                                  source=parse_qs_bytes(self.request.query),
                                  strip=strip)


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')
