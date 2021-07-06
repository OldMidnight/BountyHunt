from sqlalchemy.exc import IntegrityError
import re, requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity, create_refresh_token,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash
from BountyHunt.models import User, Bounty

bp = Blueprint('auth', __name__, url_prefix="/auth")

def bounty_resource_fn(user_id, params):
  """
  bounty_resource_fn checks if a user owns a given bounty

  :param user_id: The user to check
  :param params: A dictionary containing the bounty_url to check
  """
  bounty = Bounty.query.filter_by(user_id=user_id, url=params['bounty_url']).first()
  return True if bounty else False

@bp.route('/register', methods=('POST',))
def register():
  """
  register creates a new user and authenticates them, returning valid authentication cookies
  """
  data = request.get_json()
  email = data['email'].lower()
  password = data['password']
  username = data['username'].lower()

  errors = []

  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
    errors.append('Invalid email format.')
  if len(password) < 8:
    errors.append('Password is too short.')
  if len(username) < 3:
    errors.append('Username is too short.')
  if len(username) > 20:
    errors.append('Username must be shorter than 20 characters.')
  if not username.isalnum():
    errors.append('Username can only contain letters and numbers.')
  if not re.search(r'\d+', password) or not re.search(r'[A-Z]+', password):
    errors.append('Invalid password format.')

  if len(errors) > 0:
    return jsonify(errors=errors), 400

  user = User.query.filter_by(email=email, username=username).first()
  if user is None:
    user = User(username=username, email=email, password=generate_password_hash(password))

    try:
      user.add()
    except IntegrityError:
      return jsonify(message='An error has ocurred.'), 400

    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)

    response = jsonify()
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 201
  else:
    return jsonify(message="Unable to create user."), 400

@bp.route('/login', methods=('POST',))
def login():
  """
  login authenticates a user using provided details. Returns valid authentication cookies.
  """
  data = request.get_json()
  username = data['username']
  password = data['password']
  user = User.authenticate(username, password)
  if user:
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)

    response = jsonify()
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 201
  else:
    return jsonify(message="Unauthorized."), 401

@bp.route('/logout', methods=('POST',))
@jwt_required()
def logout():
  """
  logout removes the authentication cookies from the response, logging the user out on the frontend
  """
  response = jsonify()
  unset_jwt_cookies(response)
  return response, 200

@bp.route('/user', methods=('GET',))
@jwt_required()
def get_user():
  """
  get_user returns a users details
  """
  user_id = get_jwt_identity()
  user = User.query.filter_by(user_id=user_id).first()
  return jsonify(
    user_id=user.user_id,
    username=user.username,
    email=user.email,
    github_access_token=user.github_access_token,
    authenticated=True
  ), 200

@bp.route('/refresh_token', methods=('POST',))
@jwt_required(refresh=True)
def refresh():
  """
  refresh creates new authentication tokens if the previous ones had expired
  """
  user_id = get_jwt_identity()
  user = User.query.filter_by(user_id=user_id).first()
  access_token = create_access_token(identity=user.user_id)

  response = jsonify()
  set_access_cookies(response, access_token)

  return response, 201

@bp.route('/res/permission', methods=('POST',))
@jwt_required()
def check_resource_permission():
  """
  check_resource_permission checks if a user has permission to access a specific resource.
  Checks are unique to each resource and are specified in spearate fucntions, accessed using a resource dictionary.
  """
  user_id = get_jwt_identity()
  resource = request.get_json()['resource']
  params = request.get_json()['params']
  
  resource_fn_map = {
    'bounty': bounty_resource_fn
  }

  return jsonify(resource_fn_map[resource](user_id, params)), 200

@bp.route('/github/token', methods=('POST',))
@jwt_required()
def get_github_access_token():
  """
  get_github_access_token creates a github access token for the current user
  """
  user_id = get_jwt_identity()
  user = User.query.filter_by(user_id=user_id).first()
  code = request.get_json()['code']
  response = requests.post('https://github.com/login/oauth/access_token', {
    'client_id': current_app.config['GITHUB_CLIENT_ID'],
    'client_secret': current_app.config['GITHUB_CLIENT_SECRET'],
    'code': code
  })

  if response.ok:
    token_details = response.text.split('&')
    access_token = token_details[0].split('=')[1]
    user.add_github_token(access_token)
    return jsonify(token=access_token), 200
  return jsonify(msg='Token could not be created'), 400