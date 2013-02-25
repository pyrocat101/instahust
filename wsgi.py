from flask import Flask, render_template, request, redirect, url_for
import settings
import re
import hmac
import hashlib
import weibo
import requests
from instagram import InstagramAPI
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


application = app = Flask(__name__)
app.instagram_api = InstagramAPI(client_id=settings.INSTAGRAM_APP_ID,
                                 client_secret=settings.INSTAGRAM_APP_SECRET)
app.weibo_api = weibo.APIClient(app_key=settings.WEIBO_APP_KEY,
                                app_secret=settings.WEIBO_APP_SECRET,
                                redirect_uri=settings.WEIBO_REDIR_URL)

def verify_payload():
    payload = request.data
    signature = request.headers['X-Hub-Signature']
    client_secret = settings.INSTAGRAM_APP_SECRET
    hashing_obj = hmac.new(client_secret.encode('utf-8'),
                           msg=payload.encode("utf-8"),
                           digestmod=hashlib.sha1)
    digest = hashing_obj.hexdigest()
    if digest != signature:
        app.logger.warning("Digest and signature differ. (%s, %s)", digest, signature)
        abort(500)


def rip_hash_tags(text):
    return re.sub(r"[#@](\S+)\s?", "", text).strip()


def post_to_weibo(media):
    r = requests.get(media.images['standard_resolution'].url)
    image = StringIO(r.content)
    text = rip_hash_tags(media.caption.text)
    author = media.user.username
    url = media.link
    weibo_text = u"#%s# %s (by %s) %s" % (settings.TAG, text, author, url)
    app.logger.info("Posting pic to weibo: %s", url)
    app.weibo_api.statuses.upload.post(status=weibo_text, pic=image)
    app.logger.info("Pic posted to weibo: %s", url)


def get_new_media(change):
    recent_media, next = app.instagram_api.tag_recent_media(count=1, tag_name=settings.TAG)
    return recent_media[0]


def post_changes():
    verify_payload()
    changes = request.json
    for change in changes:
        if change['object'] == 'tag' and change['object_id'] == settings.TAG:
            medium = get_new_media(change)
            post_to_weibo(medium)
            # we only post once
            break


@app.route('/weibo_login', methods=['GET'])
def weibo_login():
    # TODO: Put a fucking button here!
    auth_url = app.weibo_api.get_authorize_url()
    return render_template('weibo_login.html', auth_url=auth_url)


@app.route('/weibo_oauth_callback', methods=['GET'])
def weibo_oauth_callback():
    code = request.args['code']
    r = app.weibo_api.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    app.weibo_api.set_access_token(access_token, expires_in)
    return redirect(url_for('index'))


@app.route('/instagram_push_callback', methods=['GET', 'POST'])
def instagram_push_callback():
    if request.method == 'GET':
        challenge = request.args['hub.challenge']
        return challenge
    else:
        app.logger.info("Incoming push to: %s", request.path)
        post_changes()
        return '', 200


@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.debug = True
