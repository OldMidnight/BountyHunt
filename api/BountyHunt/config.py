import os
from datetime import timedelta

class Config(object):
  SECRET_KEY = os.environ['BH_SECRET_KEY']
  SECURITY_PASSWORD_SALT = os.environ['BH_SECURITY_PASSWORD_SALT']
  JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECURITY_CONFIRMABLE = True
  SECURITY_TRACKABLE = True
  JWT_TOKEN_LOCATION = ['cookies']
  JWT_COOKIE_CSRF_PROTECT = True
  JWT_CSRF_IN_COOKIES = True
  JWT_COOKIE_SAMESITE = 'Strict'
  JWT_SESSION_COOKIE = False
  STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
  STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
  GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
  GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
  SQLALCHEMY_DATABASE_URI = os.environ['BH_DATABASE_URI']

class TestConfig(Config):
  TESTING = True
  ENV = 'test'
  PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProdConfig(Config):
  DEBUG = False
  JWT_COOKIE_SECURE = True
  JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
  JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

class DevConfig(Config):
  DEBUG = True
  JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
  JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
  JWT_COOKIE_DOMAIN = '.dev.localhost'
  JWT_COOKIE_SECURE = False