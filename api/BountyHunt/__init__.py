#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from BountyHunt.endpoints import bounty, auth, payments, git
from BountyHunt.extensions import jwt
from .models import db

def create_app():
  app = Flask(__name__)
  if os.environ['FLASK_ENV'] == "development":
    app.config.from_object('BountyHunt.config.DevConfig')
    print('Starting BountyHunt with DevConfig...')
  else:
    app.config.from_object('BountyHunt.config.ProdConfig')
    print('Starting BountyHunt with ProdConfig...')
  
  CORS(app, origins='http://dev.localhost', supports_credentials=True)

  with app.app_context():
    db.init_app(app)
    db.create_all()
    print('Initialized Database')

  register_extensions(app)
  register_endpoints(app)

  @app.teardown_request
  def teardown_request(exception):
    if exception:
      db.session.rollback()
    db.session.remove()

  return app

def register_extensions(app):
  jwt.init_app(app)

def register_endpoints(app):
  app.register_blueprint(bounty.bp)
  app.register_blueprint(auth.bp)
  app.register_blueprint(payments.bp)
  app.register_blueprint(git.bp)