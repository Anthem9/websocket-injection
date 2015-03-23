import tornado.web
from views import MainHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ('/', MainHandler),
        ]
        settings = dict(debug=True,)
        tornado.web.Application.__init__(self, handlers=handlers, **settings)

