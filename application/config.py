import os
import secrets
basedir = os.path.abspath(os.path.dirname(__file__))

class LocalDevelopmentConfig():
    DEBUG = True
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "project.db")
    SECRET_KEY = secrets.token_urlsafe() #os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_REGISTER_VIEW = '/authorizing'
    SECURITY_POST_LOGIN_VIEW = '/authorizing'
    SECURITY_POST_LOGOUT_VIEW = '/'
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    SECURITY_PASSWORD_LENGTH_MIN = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE=False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    # WTF_CSRF_ENABLED = True
    # CELERY_BROKER_URL = "redis://localhost:6379/1"
    # CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    # CELERY_TIMEZONE = "Asia/Kolkata"
    # REDIS_URL = "redis://localhost:6379"
    # GMAIL_CREDS_FILE = 'GamilApi/appdev2-391904-167712a96be2.json'
    # SECURITY_TRACKABLE = True
    # SECURITY_UNAUTHORIZED_VIEW = None
    # SECURITY_USERNAME_ENABLE = True
    # SECURITY_USERNAME_REQUIRED = True
    # SECURITY_CHANGEABLE = True
    # SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
