import tornado.gen
from tornado.escape import parse_qs_bytes
from core.base import BaseHandler
from core.exceptions import UnexpectedReuqestDataException, InvalidWebSocketURLException


class SQLMapHandler(BaseHandler):
    def get(self):
        self.post()

    @tornado.gen.coroutine
    def post(self):
        url = self.get_argument('url', default=None)
        if not url:
            raise UnexpectedReuqestDataException
        if not url.startswith('ws://') and not url.startswith('wss://'):
            raise InvalidWebSocketURLException
        self.connect(url)

    def get_argument(self, name, default=None, strip=True):
        return self._get_argument(name, default=default,
                                  source=parse_qs_bytes(self.request.query),
                                  strip=strip)


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')
