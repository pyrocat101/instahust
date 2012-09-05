from google.appengine.ext import db


class Profile(db.Model):
    full_name = db.StringProperty()
    ig_user_id = db.StringProperty()
    ig_username = db.StringProperty()
    ig_access_token = db.StringProperty()

    def instagram_connected(self):
        return (self.ig_access_token and self.ig_user_id)