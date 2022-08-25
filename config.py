import os

class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = int(465)
    MAIL_USERNAME = 'mobile.de.scrape.team@gmail.com'
    MAIL_PASSWORD = 'hjrndngvkpfjntod'
    MOBILE_MAIL_SUBJECT_PREFIX = '[Mobile DE Scraper] '
    MOBILE_MAIL_SENDER = 'Mobile DE Scrape Admin <Mobile.DE.Scrape.Team@gmail.com>'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root:Einstein1988++@127.0.0.1:3306/mobile_de?charset=utf8mb4'

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://saramich$mobile_de?charset=utf8mb4'

config = {
'development': DevConfig,
'production': ProdConfig,
'default': DevConfig
}