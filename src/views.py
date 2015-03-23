import websocket
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url', default=None)
        data = self.get_argument('data', default=None)
        if not url or not data:
            raise Exception('Usage: sqlmap.py -u "http://%s/?url=[target]&data=[sql'
                            'i]" -p data' % self.request.host)
        if not url.startswith('ws://') and not url.startswith('wss://'):
            raise Exception('Invalid WebSocket Url, example: ws://127.0.0.1/chat')

        print 'Request Payload: %s' % data
        ws = websocket.WebSocket(sslopt={'cert_reqs': 0})
        ws.connect(url)
        ws.send(data)
        self.write(ws.recv())
        self.finish()