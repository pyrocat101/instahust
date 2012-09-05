from google.appengine.ext import webapp

import logging
import settings

from weibo import APIClient
from instahust.models import Profile
from lilcookies import LilCookies


class WeiboAuth(webapp.RequestHandler):
    def get(self):
        #cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        #ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")

        logging.info(settings.INSTAGRAM_CONFIG)
        logging.info(settings.WEIBO_CONFIG)
        weibo_client = APIClient(**settings.WEIBO_CONFIG)
        #dba = dropbox_auth.Authenticator(settings.DROPBOX_CONFIG)
        #req_token = dba.obtain_request_token()

        #profiles = Profile.all()
        #profiles.filter("ig_user_id =", ig_user_id)
        #profile = profiles.get()

        #if not profile:
        #    self.redirect("/connect")
        #    return

        #profile.db_oauth_token_key = settings.WEIBO_CONFIG["app_key"]
        #profile.db_oauth_token_secret = settings.WEIBO_CONFIG["app_secret"]
        #profile.put()

        authorize_url = weibo_client.get_authorize_url()

        self.redirect(authorize_url)


class WeiboDisconnect(webapp.RequestHandler):
    def get(self):
        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")

        profiles = Profile.all()
        profiles.filter("ig_user_id =", ig_user_id)
        profile = profiles.get()

        if profile:
            profile.weibo_access_token_key = None
            profile.weibo_access_token_expire = None
            profile.put()

        self.redirect("/")


class WeiboCallback(webapp.RequestHandler):
    def get(self):
        code = self.request.get('code')
        weibo_client = APIClient(**settings.WEIBO_CONFIG)
        logging.info("OAuth2 Code: " + code)
        r = weibo_client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        logging.info("OAuth2 Access Token: " + access_token)

        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")
        logging.info("UserID: " + ig_user_id)
        profiles = Profile.all()
        profiles.filter("ig_user_id =", ig_user_id)
        profile = profiles.get()

        if not profile:
            logging.error("No profile!")
            self.redirect("/connect")
            return

        profile.weibo_access_token_key = access_token
        profile.weibo_access_token_expire = expires_in
        profile.put()

        self.redirect("/connect")

    # def get(self):
    #     from oauth import oauth

    #     dba = dropbox_auth.Authenticator(settings.DROPBOX_CONFIG)

    #     token = self.request.get("oauth_token")
    #     profile = Profile.all().filter("db_oauth_token_key =", token).get()

    #     if not profile:
    #         self.redirect("/connect")
    #         return

    #     oauth_token = oauth.OAuthToken(
    #                                    key = profile.db_oauth_token_key,
    #                                    secret = profile.db_oauth_token_secret)

    #     verifier = settings.DROPBOX_CONFIG['verifier']
    #     access_token = dba.obtain_access_token(oauth_token, verifier)

    #     profile.db_access_token_key = access_token.key
    #     profile.db_access_token_secret = access_token.secret
    #     profile.put()

    #     self.redirect("/connect")