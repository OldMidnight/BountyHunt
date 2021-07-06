import requests
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from BountyHunt.models import User, Bounty, Category, BountyApplication, Investment, BountySubmissionApproval, GithubRepository
from BountyHunt.helpers import to_cents

bp = Blueprint('bounty', __name__, url_prefix="/bounty")

@bp.route('/', methods=('POST',))
@jwt_required()
def create_bounty():
  """
  create_bounty creates a bounty using details given in request.
  Creates an entry in the Investment table for the initial contribtion.
  """
  user_id = get_jwt_identity()
  req_bounty = request.get_json()
  req_bounty['amount'] = to_cents(req_bounty['amount'])
  
  bounty = Bounty.new_from_dict(req_bounty, error_on_extra_keys=False, drop_extra_keys=True)
  bounty.user_id = user_id

  for category in req_bounty['selected_categories']:
    b_category = Category.query.filter_by(category_id=category[1]).first()
    bounty.categories.append(b_category)

  try:
    bounty.add()
  except IntegrityError:
    return jsonify(message='An error has ocurred.'), 400

  investment = Investment(created=bounty.created, amount=bounty.amount, currency_code=bounty.currency_code, bounty_id=bounty.bounty_id, user_id=user_id)

  try:
    investment.add()
  except Exception as e:
    print(e)
    return jsonify(message='An error has ocurred. Please contact support.'), 400

  return jsonify(), 201

@bp.route('/list', methods=('GET',))
@jwt_required(optional=True)
def get_all_bounty():
  """
  get_all_bounty returns a list of all bounties that fit into the given filters.

  :request_param u: Filter bounties by username
  :request_param i: Filter bountis by those the user has invested in
  :request_param completed: Filter bounties by whether they have been completed
  :request_param category: Filters bounties by a specified category id
  """
  username = request.args.get('u', type=str)
  invest = request.args.get('i', default=False, type=bool)
  completed = request.args.get('completed', default=False, type=bool)
  category = request.args.get('category', default=0, type=int)
  cgs = Category.query.filter_by(category_id=category).first()

  # update each bounty to include the author of the bounty
  bounties = []

  if username:
    user = User.query.filter_by(username=username).first()

    if invest:
      investments = Investment.query.distinct(Investment.bounty_id).filter_by(user_id=user.user_id).all()
      for investment in investments:
        if investment.bounty_id:
          bounty_dict = investment.bounty.to_dict(max_nesting=2)
          bounty_dict.update({'author': user.username})
          bounty_dict.pop('applications')
          bounties.append(bounty_dict)

    elif completed:
      bounty_list = Bounty.query.filter_by(assigned_user_id=user.user_id, completed=completed).all()
      for bounty in bounty_list:
        bounty_dict = bounty.to_dict(max_nesting=2)
        bounty_dict.update({'author': user.username})
        bounty_dict.pop('applications')
        bounties.append(bounty_dict)

    else:
      bounty_list = Bounty.query.filter_by(user_id=user.user_id).all()
      for bounty in bounty_list:
        bounty_dict = bounty.to_dict(max_nesting=2)
        bounty_dict.update({'author': user.username})
        bounty_dict.pop('applications')
        bounties.append(bounty_dict)

  else:
    for bounty in cgs.bounties:
      if not bounty.assigned_user_id:
        user = bounty.user.to_dict()
        bounty_dict = bounty.to_dict(max_nesting=2)
        bounty_dict.update({'author': user['username']})
        bounty_dict.pop('applications')
        bounties.append(bounty_dict)
  return jsonify(bounties), 200

@bp.route('/<bounty_url>', methods=('GET',))
@jwt_required(optional=True)
def get_bounty(bounty_url):
  """
  get_bounty returns a single bounty using the given bounty_url route parameter

  :param bounty_url: A bounties unique URL
  """
  user_id = get_jwt_identity()
  show_details = request.args.get('show_details', default=False, type=bool)
  bounty = Bounty.query.filter_by(url=bounty_url).first()
  if bounty:
    b_application = BountyApplication.query.filter_by(user_id=user_id, bounty_id=bounty.bounty_id).first()
    has_application = b_application is not None

    # Updates applications to include the user details of each applicant
    applications = []
    investments = []

    for applicant in bounty.applications:
      application_dict = applicant.to_dict()
      application_dict['username'] = applicant.user.username
      application_dict['user_id'] = applicant.user.user_id
      
      applications.append(application_dict)

    for investment in bounty.investments:
      investment_dict = investment.to_dict()
      investment_dict['username'] = investment.user.username
      investment_dict['user_id'] = investment.user.user_id
      
      investments.append(investment_dict)

    author = bounty.user.username  
    bounty = bounty.to_dict(max_nesting=2 if show_details else 0)
    bounty['applications'] = applications
    bounty['investments'] = investments
    bounty['author'] = author

    return jsonify(bounty=bounty, has_application=has_application), 200
  return jsonify(msg='bounty not found.'), 404

@bp.route('/git/<owner>/<repo_name>/issues/<issue>', methods=('GET',))
@jwt_required(optional=True)
def get_git_bounty(owner, repo_name, issue):
  """
  get_git_bounty returns a git based bounty using the given route parameters.
  Fetches git issue details by querying github API

  :param owner: The owner of the git repo the issue belongs to
  :param repo_name: The name of the repo the issue belongs to
  :param issue: The title of the issue the bounty is based on
  """
  user_id = get_jwt_identity()
  url = f'{owner}/{repo_name}/issues/{issue}'
  bounty = Bounty.query.filter_by(url=url).first()

  if bounty:
    repo = GithubRepository.query.filter_by(full_name=f'{owner}/{repo_name}').first()
    github_access_token = f'token {repo.user.github_access_token}'
    response = requests.get(f'https://api.github.com/repos/{url}', headers={'Authorization': github_access_token})
    comments_response = requests.get(f'https://api.github.com/repos/{url}/comments', headers={'Authorization': github_access_token})

    if response.ok and comments_response.ok:
      b_application = BountyApplication.query.filter_by(user_id=user_id, bounty_id=bounty.bounty_id).first()
      has_application = b_application is not None

      # Updates the applications key to include the user details of each applicant
      applications = []
      investments = []

      for applicant in bounty.applications:
        application_dict = applicant.to_dict()
        application_dict['username'] = applicant.user.username
        application_dict['user_id'] = applicant.user.user_id
        
        applications.append(application_dict)

      for investment in bounty.investments:
        investment_dict = investment.to_dict()
        investment_dict['username'] = investment.user.username
        investment_dict['user_id'] = investment.user.user_id
        
        investments.append(investment_dict)

      author = bounty.user.username  
      bounty = bounty.to_dict(max_nesting=2)
      bounty['applications'] = applications
      bounty['investments'] = investments
      bounty['author'] = author

      return jsonify(bounty=bounty, issue=response.json(), comments=comments_response.json(), has_application=has_application), 200

    return jsonify(msg=response.text), 400
  return jsonify(msg='bounty not found.'), 404

@bp.route('/assign', methods=('PUT',))
@jwt_required()
def assign_bounty():
  """
  assign_bounty assigns a bounty to a specified user
  """
  user_id = get_jwt_identity()
  data = request.get_json()
  bounty = Bounty.query.filter_by(url=data['bounty_url'], user_id=user_id).first()
  if bounty:
    assigned_user_id = data['assigned_user_id']
    if assigned_user_id == user_id:
      return jsonify(msg='You cannot assign a bounty to yourself'), 400
    bounty.assign(assigned_user_id)
    return jsonify(msg='Bounty assigned to Hunter!'), 200

@bp.route('/hunter', methods=('GET',))
@jwt_required(optional=True)
def get_assigned_hunter():
  bounty_url = request.args.get('bounty_url', type=str)
  bounty = Bounty.query.filter_by(url=bounty_url).first()
  assigned_user = User.query.filter_by(user_id=bounty.assigned_user_id).first()

  user_dict = {
    'username': assigned_user.username,
    'email': assigned_user.email
  }
  
  return jsonify(user_dict), 200

@bp.route('/apply', methods=('POST',))
@jwt_required()
def apply_bounty():
  """
  apply_bounties creates an application to a bounty for the current user
  """
  user_id = get_jwt_identity()
  data = request.get_json()
  bounty = Bounty.query.filter_by(url=data['bounty_url']).first()
  if bounty.user_id == user_id:
    return jsonify(message='You cannot apply to your own bounty!'), 400
  b_application = BountyApplication.query.filter_by(user_id=user_id, bounty_id=bounty.bounty_id).first()

  if b_application is not None:
    return jsonify(msg='You have already applied to this bounty.'), 409

  b_application = BountyApplication(application_text=data['application_text'], created=data['created'], bounty_id=bounty.bounty_id, user_id=user_id)

  try:
    b_application.add()
  except:
    return jsonify(message='An error has ocurred.'), 400
  
  return jsonify(), 201

@bp.route('/invest', methods=('POST',))
@jwt_required()
def invest_bounty():
  """
  invest_bounty creates an investment record for a bounty by the current user
  """
  req_data = request.get_json()
  investment = req_data['investment']
  amount = to_cents(investment['amount'])
  bounty = Bounty.query.filter_by(url=req_data['bounty_url']).first()
  user_id = get_jwt_identity()
  investment = Investment(created=investment['created'], amount=amount, currency_code=investment['currency_code'], bounty_id=bounty.bounty_id, user_id=user_id)

  try:
    investment.add()
  except Exception as e:
    print(e)
    return jsonify(message='An error has ocurred. Please contact support.'), 400

  bounty.update_bounty_amount(amount)

  return jsonify(), 204

@bp.route('/invest', methods=('GET',))
@jwt_required()
def get_user_investment():
  """
  get_user_investment returns all investments the current user has made into a specified bounty
  """
  bounty_url = request.args.get('bounty_url', type=str)
  user_id = get_jwt_identity()
  bounty = Bounty.query.filter_by(url=bounty_url).first()
  investments = Investment.query.filter_by(user_id=user_id, bounty_id=bounty.bounty_id).all()

  amount = 0
  for investment in investments:
    amount += investment.amount

  return jsonify(amount), 200

@bp.route('/submission', methods=('PUT',))
@jwt_required()
def submit_bounty():
  """
  submit_bounty creates a submission for a bounty by the current user
  """
  user_id = get_jwt_identity()
  data = request.get_json()
  submission = data['submission']
  bounty = Bounty.query.filter_by(url=data['bounty_url']).first()
  if user_id != bounty.assigned_user_id:
    return jsonify(msg='User not allowed'), 403

  try:
    bounty.submit(submission['description'], submission['link'])
  except Exception as e:
    print(e)
    return jsonify(msg='Could not submit bounty'), 400

  return jsonify(msg='Bounty submitted'), 200

@bp.route('/submission/approval', methods=('POST',))
@jwt_required()
def approve_submission():
  """
  approve_submission creates a BountyApproval record for a specified bounty by the current user
  """
  data = request.get_json()
  bounty = Bounty.query.filter_by(url=data['bounty_url']).first()
  user_id = get_jwt_identity()

  bounty_approval = BountySubmissionApproval(bounty_id=bounty.bounty_id, user_id=user_id, is_approved=data['is_approved'], decision_datetime=data['decision_datetime'])

  try:
    bounty_approval.add()
  except:
    return jsonify(msg='An error occurred'), 400

  approval_list = []
  for investment in bounty.investments:
    bounty_approval = BountySubmissionApproval.query.filter_by(user_id=investment.user_id, bounty_id=bounty.bounty_id).first()
    if bounty_approval:
      approval_list.append(True)
    else:
      approval_list.append(False)
  
  if all(approval_list):
    bounty.complete(data['decision_datetime'])
  
  return jsonify(msg='Decision received'), 201

@bp.route('/categories', methods=('GET',))
def get_categories():
  """
  get_categories returns a list of all categories formatted as [[category_name, category_id]]
  """
  categories = Category.query.all()
  return jsonify([[c.name, c.category_id] for c in categories]), 200

@bp.route('/user/<username>/current', methods=('GET',))
@jwt_required()
def get_user_current_bounty(username):
  user = User.query.filter_by(username=username).first()
  current_bounty = None
  for bounty in user.assigned_bounties:
    if not bounty.completed:
      author = bounty.user.username
      current_bounty = bounty.to_dict()
      current_bounty['author'] = author

  return jsonify(current_bounty), 200

@bp.route('/<username>/approval', methods=('GET',))
@jwt_required()
def get_user_approval(username):
  """
  get_user_approval returns the approval status on a specified bounty by the provided user

  :param username: The user for which to check approval
  """
  bounty_url = request.args.get('bounty_url', type=str)
  user = User.query.filter_by(username=username).first()
  bounty = Bounty.query.filter_by(url=bounty_url).first()
  approval = BountySubmissionApproval.query.filter_by(user_id=user.user_id, bounty_id=bounty.bounty_id).first()
  if approval:
    approval = approval.to_dict()
    return jsonify(is_approved=approval['is_approved'], decision_datetime=approval['decision_datetime']), 200
  else:
    return jsonify(is_approved=False, decision_datetime=None), 200