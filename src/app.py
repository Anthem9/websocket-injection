import tornado.web
from views import handlers as handlers_


class Application(tornado.web.Application):
    def __init__(self):
        handlers = handlers_
        settings = dict(debug=True,)
        tornado.web.Application.__init__(self, handlers=handlers, **settings)

