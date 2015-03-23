import logging
from base import BaseHandler


class SQLMapHandler(BaseHandler):
    def get(self):
        url = self.get_argument('url', default=None)
        data = self.get_argument('data', default=None)
        if not url or not data:
            raise Exception('Usage: sqlmap.py -u "http://%s/sqlmap?url=[target'
                            ']&data=[sqli]" -p data' % self.request.host)
        if not url.startswith('ws://') and not url.startswith('wss://'):
            raise Exception('Invalid WebSocket Url, example: ws://127.0.0.1/')

        logging.info('Request payload: %s' % data)

        try:
            self.websocket.connect(url)
            self.websocket.send(data)
            data = self.websocket.recv()
        except Exception, e:
            logging.error('Error: %s' % str(e))
            self.response({'error': str(e)})

        self.response(data)


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')
