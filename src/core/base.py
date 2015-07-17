import time
import logging
import thread
import websocket
import tornado.web
import signal
from tornado.template import Loader
from core.exceptions import TimeoutWithoutResponseException
from websocket._exceptions import WebSocketConnectionClosedException


def timeout_handler(signum, frame):
    logging.error('Time exceeded when waiting for response.')
    raise TimeoutWithoutResponseException


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
    _instance = None
    message_queue = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebSocketAppMixin, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def on_message(self, websocket, message):
        logging.info('Recv: %s' % message)
        self.message_queue.append(message)

    def on_close(self, websocket):
        logging.warning('Connection closed.')
        self.response('\n'.join(self.message_queue))
        self.message_queue = []

    def on_error(self, websocket, error):
        logging.error('Error: %s' % error)
        error_message = '-' * 20 + '\nError: %s\n' % error + '-' * 20
        self.message_queue.append(error_message)

    def on_open(self, websocket):
        def run():
            try:
                data = self.get_argument('data')
                logging.info('Send: %s' % data)
                websocket.send(data)
                time.sleep(0.1)
                websocket.keep_running = False
                websocket.close()
            except WebSocketConnectionClosedException:
                pass
        thread.start_new_thread(run, ())

    def connect(self, url):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(20)
        logging.info('Connecting: %s' % url)
        # websocket.enableTrace(True)
        self.client = websocket.WebSocketApp(url=url,
                                             on_message=self.on_message,
                                             on_close=self.on_close,
                                             on_error=self.on_error)
        self.client.on_open = self.on_open
        self.client.run_forever()


class BaseHandler(tornado.web.RequestHandler, WebSocketAppMixin):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def response(self, data):
        logging.info('Response: %s...' % data.replace('\n', ' ')[0:40])
        self.write(data)
        self.finish()

    def render(self, template, **kwargs):
        loader = Loader('templates')
        self.write(loader.load(template).generate(**kwargs))
        self.finish()
