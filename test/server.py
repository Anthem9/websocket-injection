import logging
import MySQLdb
import json
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.websocket
import tornado.options


class Storage(dict):
    def __getitem__(self, item):
        return self[item]

    def __setitem__(self, key, value):
        self[key] = value


class BaseSocketHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        self.session = Storage()
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="test", charset="utf8")
        self.db = db.cursor()

        tornado.websocket.WebSocketHandler.__init__(self,application, request, **kwargs)


class WebSocketHandler(BaseSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        self.session.id = str(id(self))
        self.session.times = 0
        data = self.get_argument('data', default=None)
        logging.warning('Request(connect): %s' % self.session.id)
        try:
            self.db.execute("select table_name from information_schema.tables where table_schema='%s'" % data)
            data = self.db.fetchall()[0]
            self.send_message({'text': data[0]})
        except Exception, e:
            self.send_message({'text': str(e)})
        self.send_message('aaa')

    def on_close(self):
        logging.warning('Close: %s' % self.session.id)
        self.close()

    def on_message(self, message):
        logging.info('Recv(%d): %s' % (self.session.times, message))
        #if self.session.times == 1:
        try:
            self.db.execute("select table_name from information_schema.tables where table_schema='%s'" % message)
            data = self.db.fetchall()[0]
            self.send_message({'text': data[0]})
        except Exception, e:
            self.send_message({'text': str(e)})

    def send_message(self, message):
        logging.info('Send: %s' % message)
        self.write_message(message)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ('/', WebSocketHandler),
        ]
        settings = dict(debug=True,)
        tornado.web.Application.__init__(self, handlers=handlers, **settings)


if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.instance().start()
