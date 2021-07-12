SPOTIFY_CLIENT_ID = "3ec61776aa7b47eab48342ce4fd16922"
SPOTIFY_CLIENT_SECRET = "888251bf9aad42a9b2751fa02ddf55cb"

class ProdConfig():
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig():
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    
