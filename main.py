from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


from google.appengine.dist import use_library
use_library('django', '0.96')


from instahust.handlers import WelcomeHandler, ConnectHandler
# from instagram.handlers import (InstagramAuth, InstagramCallback, \
#                                 InstagramSubscribe, InstagramPushCallback, \
#                                 InstagramDisconnect, InstagramLoadUser)
from instagram.handlers import (InstagramAuth, InstagramCallback, \
                                InstagramPushCallback, \
                                InstagramDisconnect, InstagramLoadUser)
from weibo.handlers import WeiboAuth, WeiboCallback, WeiboDisconnect
#from dropbox.handlers import DropboxAuth, DropboxCallback, DropboxDisconnect


from patches import webapp_patches # TODO make this better/automated


application = webapp.WSGIApplication([
    ("/", WelcomeHandler),
    ("/connect", ConnectHandler),
    ("/instagram/auth", InstagramAuth),
    ("/instagram/callback", InstagramCallback),
#    ("/instagram/subscribe", InstagramSubscribe),
    ("/instagram/push_callback", InstagramPushCallback),
    ("/instagram/disconnect", InstagramDisconnect),
    ("/instagram/load_user", InstagramLoadUser),
    ("/weibo/auth", WeiboAuth),
    ("/weibo/callback", WeiboCallback),
    ("/weibo/disconnect", WeiboDisconnect)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
