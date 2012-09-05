from google.appengine.ext import webapp

import settings

from lilcookies import LilCookies
from instahust.models import Profile


class WelcomeHandler(webapp.RequestHandler):
    def get(self):
        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")

        profiles = Profile.all()
        profiles.filter("ig_user_id =", ig_user_id)
        profile = profiles.get()

        if profile and profile.fully_connected():
            self.render_template("connected.html")
        else:
            self.render_template("not_connected.html", {
                "profile": profile,
                "client_id": settings.INSTAGRAM_CONFIG["client_id"]
            })


class ConnectHandler(webapp.RequestHandler):
    def get(self):
        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")


        profiles = Profile.all()
        profiles.filter("ig_user_id =", ig_user_id)
        profile = profiles.get()

        if profile and profile.weibo_access_token_key and \
                       profile.weibo_access_token_expire:
            self.redirect("/")
        elif profile and not (profile.weibo_access_token_key or
                              profile.weibo_access_token_expire):
            self.redirect("/weibo/auth")
        else:
            self.redirect("/instagram/auth")
