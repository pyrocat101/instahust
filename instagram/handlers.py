# -*- coding: utf-8 -*-

from google.appengine.ext import webapp

import settings

from instagram.client import InstagramAPI

from instahust.models import Profile
from lilcookies import LilCookies


class InstagramAuth(webapp.RequestHandler):
    def get(self):
        api = InstagramAPI(**settings.INSTAGRAM_CONFIG)
        self.redirect(api.get_authorize_url())


class InstagramDisconnect(webapp.RequestHandler):
    def get(self):
        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        ig_user_id = cookieutil.get_secure_cookie(name = "ig_user_id")

        profiles = Profile.all()
        profiles.filter("ig_user_id =", ig_user_id)
        profile = profiles.get()

        if profile:
            profile.delete()

        self.redirect("/")


class InstagramCallback(webapp.RequestHandler):
    def get(self):
        instagram_client = InstagramAPI(**settings.INSTAGRAM_CONFIG)

        code = self.request.get("code")
        access_token = instagram_client.exchange_code_for_access_token(code)

        instagram_client = InstagramAPI(access_token = access_token)

        user = instagram_client.user("self")

        profiles = Profile.all()
        profiles.filter("ig_user_id = ", user.id)
        profile = (profiles.get() or Profile())

        profile.full_name = (user.full_name or user.username)
        profile.ig_user_id = user.id
        profile.ig_username = user.username
        profile.ig_access_token = access_token
        profile.put()

        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        cookieutil.set_secure_cookie(
                name = "ig_user_id",
                value = user.id,
                expires_days = 365)

        self.redirect("/connect")

class InstagramLoadUser(webapp.RequestHandler):
    def get(self):
        ig_user_id = self.request.get("ig_user_id")

        if not ig_user_id:
            self.redirect("/connect")

        instagram_client = InstagramAPI(**settings.INSTAGRAM_CONFIG)

        access_token = instagram_client.exchange_user_id_for_access_token(ig_user_id)

        instagram_client = InstagramAPI(access_token = access_token)

        user = instagram_client.user("self")

        profiles = Profile.all()
        profiles.filter("ig_user_id = ", user.id)
        profile = (profiles.get() or Profile())

        profile.full_name = (user.full_name or user.username)
        profile.ig_user_id = user.id
        profile.ig_username = user.username
        profile.ig_access_token = access_token
        profile.put()

        cookieutil = LilCookies(self, settings.COOKIE_SECRET)
        cookieutil.set_secure_cookie(
                name = "ig_user_id",
                value = user.id,
                expires_days = 365)

        self.redirect("/")


class InstagramPushCallback(webapp.RequestHandler):
    def get(self):
        challenge = self.request.get("hub.challenge")
        self.response.out.write(challenge)


    def post(self):
        import logging
        import hashlib
        import hmac
        import logging
        import re
        from StringIO import StringIO
        from time import time
        from urllib2 import urlopen
        from django.utils import simplejson

        from weibo import APIClient

        payload = self.request.body

        # verify payload
        signature = self.request.headers['X-Hub-Signature']
        client_secret = settings.INSTAGRAM_CONFIG['client_secret']
        hashing_obj= hmac.new(client_secret.encode("utf-8"),
            msg = payload.encode("utf-8"),
            digestmod = hashlib.sha1)
        digest = hashing_obj.hexdigest()

        if digest != signature:
            logging.info("Digest and signature differ. (%s, %s)"
                % (digest, signature))
            return

        changes = simplejson.loads(payload)
        for change in changes:
            profiles = Profile.all()
            profiles.filter("ig_user_id =", change['object_id'])
            profile = profiles.get()

            if not profile:
                logging.info("Cannot find profile %s", change['object_id'])
                continue

            instagram_client = InstagramAPI(
                    access_token = profile.ig_access_token)

            media, _ = instagram_client.user_recent_media(count = 1)
            media = media[0]

            # filter
            if "instahust" not in map(lambda x: x.name, media.tags): return

            media_file = urlopen(media.images['standard_resolution'].url)
            media_data = media_file.read()

            pic_file = StringIO(media_data)
            weibo_text = media.caption.text
            # rip hashtag & strip whitespace
            weibo_text = re.sub(r"#(\w+)", "", weibo_text).strip()
            instagram_author = media.user.username
            instagram_url = media.link

            weibo_content = u"#instahust#%s (by %s) %s" % \
                            (weibo_text, instagram_author, instagram_url)

            weibo_client = APIClient(settings.WEIBO_GSID)
            weibo_client.post(content=weibo_content, pic=pic_file)
