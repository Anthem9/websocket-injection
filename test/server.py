import logging
import MySQLdb
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


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        self.send_message("Hello")
        self.send_message("Hello2")

    def on_message(self, message):
        logging.info('Recv: %s' % message)
        self.send_message(message)
        self.session = Storage()
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="test", charset="utf8")
        cur = db.cursor()
        try:
            sql = "select table_name from information_schema.tables where table_schema='%s'" % message
            logging.info('Execute: %s' % sql)
            cur.execute(sql)
            data = cur.fetchall()[0]
            self.send_message({'text': data[0]})
        except Exception, e:
            self.send_message({'text': str(e)})
        cur.close()
        db.close()
        self.close()

    def on_close(self):
        logging.warning('Close')

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
