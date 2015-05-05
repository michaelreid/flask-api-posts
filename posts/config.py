class DevelopmentConfig(object):
    DATABASE_URI = "postgresql://m:juniordevs1@localhost:5432/posts"
    DEBUG = True

class TestingConfig(object):
    DATABASE_URI = "postgresql://m:juniordevs1@localhost:5432/posts-test"
    DEBUG = True
    
class TravisConfig(object):
    DATABASE_URI = "postgresql://localhost:5432/posts-test"
    DEBUG = False
    SECRET_KEY = "Not secret"
    
