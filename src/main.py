import logging
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
from app import Application


if __name__ == '__main__':
    define('port', default=8888, help='Port listened')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    logging.basicConfig(format='%(asctime) %(message)s')
    logging.warning('WebSocket Injection Proxy Listening on 0.0.0.0:%d' % options.port)
    tornado.ioloop.IOLoop.instance().start()
