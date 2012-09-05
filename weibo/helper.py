def load_config(config_file):
    from dropbox import auth
    return auth.Authenticator.load_config(config_file)


def authenticated_client():
    import settings
    from weibo import APIClient

    client = APIClient(**settings.WEIBO_CONFIG)
    client.set_access_token(settings.WEIBO_ACCESS_TOKEN,
    						settings.WEIBO_ACCESS_TOKEN_EXPIRE)

    return client