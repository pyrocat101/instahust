from google.appengine.ext import db


class Profile(db.Model):
    full_name = db.StringProperty()
    ig_user_id = db.StringProperty()
    ig_username = db.StringProperty()
    ig_access_token = db.StringProperty()
    #db_oauth_token_key = db.StringProperty()
    #db_oauth_token_secret = db.StringProperty()
    weibo_access_token_key = db.StringProperty()
    weibo_access_token_expire = db.IntegerProperty()
    #db_access_token_secret = db.StringProperty()

    def weibo_connected(self):
        return (self.weibo_access_token_key and self.weibo_access_token_expire)


    def instagram_connected(self):
        return (self.ig_access_token and self.ig_user_id)


    def fully_connected(self):
        return (self.weibo_connected() and self.instagram_connected())