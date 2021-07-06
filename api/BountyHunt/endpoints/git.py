from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended.utils import get_jwt_identity
from BountyHunt.models import GithubRepository, Bounty, User
import requests

bp = Blueprint('git', __name__, url_prefix="/git")

@bp.route('/github/repos', methods=('POST',))
@jwt_required()
def add_github_repos():
  """
  add_github_repos adds a list of repositories to the GithubRepository table.
  """
  user_id = get_jwt_identity()
  repos = request.get_json()
  try:
    GithubRepository.add_repos(repos, user_id)
  except Exception as e:
    print(e)
    return jsonify(msg='An error occurred adding these repositories.'), 400
  return jsonify(msg='Repositories added successfully'), 201

@bp.route('/github/user/repos', methods=('GET',))
@jwt_required()
def get_user_added_repos():
  """
  get_user_added_repos returns a list of repositories belonging to the current user.
  A request is made to the Github API using the users unique access token.
  """
  user_id = get_jwt_identity()
  user = User.query.filter_by(user_id=user_id).first()
  github_access_token = f'token {user.github_access_token}'
  github_user_response = requests.get(f'https://api.github.com/user', headers={'Authorization': github_access_token})
  git_repos = []
  if github_user_response.ok:
    github_user = github_user_response.json()['login']
    response = requests.get(f'https://api.github.com/users/{github_user}/repos', headers={'Authorization': github_access_token})
    git_repos = response.json() if response.ok else []
  return jsonify(git_repos), 200

@bp.route('/github/repos', methods=('GET',))
def get_repos():
  """
  get_repos returns a list of all repos added to BountyHunt by users. Can be filtered using a search query parameter.

  :request_param q: a search string to filter repos with
  """
  q = request.args.get('q', type=str)
  per_page = request.args.get('per_page', type=int)
  page = request.args.get('page', type=int)
  if q:
    repos = GithubRepository.query.filter(GithubRepository.full_name.like('%' + q + '%')).paginate(page, per_page, False)
  else:
    repos = GithubRepository.query.paginate(page, per_page, False)
  return jsonify(total=repos.total, items=[repo.to_dict() for repo in repos.items]), 200

@bp.route('/github/repo', methods=('GET',))
@jwt_required()
def get_repo():
  """
  get_repo returns a github repository including issues in that repository. Issues can be filtered using a search query parameter.

  :request_param q: a search string to filter issues with
  """
  full_name = request.args.get('full_name', type=str)
  q = request.args.get('q', type=str)
  repo = GithubRepository.query.filter_by(full_name=full_name).first()
  github_access_token = f'token {repo.user.github_access_token}'
  repo_response = requests.get(f'https://api.github.com/repos/{full_name}', headers={'Authorization': github_access_token})
  issues_response = requests.get(f'https://api.github.com/search/issues?q={q}', headers={'Authorization': github_access_token})
  if repo_response.ok and issues_response.ok:
    amount = 0
    issues = issues_response.json()
    for issue in issues['items']:
      bounty = Bounty.query.filter_by(title=issue['title'], is_git_bounty=True).first()
      if bounty:
        issue['is_bounty'] = True
        issue['bounty_amount'] = bounty.amount
        amount += bounty.amount
    repo = repo_response.json()
    repo['amount'] = amount
    return jsonify(repo=repo, issues=issues, amount=amount), 200
  return jsonify(msg='An error occured fetching Github repo details'), 400

@bp.route('/github/repo/issues/<issue_number>', methods=('GET',))
@jwt_required()
def get_issue(issue_number):
  """
  get_issue returns the details of a github issue.
  """
  full_name = request.args.get('full_name', type=str)
  repo = GithubRepository.query.filter_by(full_name=full_name).first()
  github_access_token = f'token {repo.user.github_access_token}'
  response = requests.get(f'https://api.github.com/repos/{full_name}/issues/{issue_number}', headers={'Authorization': github_access_token})
  comments_response = requests.get(f'https://api.github.com/repos/{full_name}/issues/{issue_number}/comments', headers={'Authorization': github_access_token})
  if response.ok and comments_response.ok:
    return jsonify(issue=response.json(), comments=comments_response.json()), 200
  return jsonify(msg='An error occured fetching issue'), 400

@bp.route('/github/search/issues', methods=('GET',))
@jwt_required()
def search_github_issues():
  """
  search_github_issues searches a repositories issues using a gives search string parameter.
  """
  q = request.args.get('q', type=str)
  full_name = '/'.join(request.referrer.split('/')[-2:])
  repo = GithubRepository.query.filter_by(full_name=full_name).first()
  github_access_token = f'token {repo.user.github_access_token}'
  response = requests.get(f'https://api.github.com/search/issues?q={q}', headers={'Authorization': github_access_token})

  if response.ok:
    issues = response.json()
    for issue in issues['items']:
      bounty = Bounty.query.filter_by(title=issue['title'], is_git_bounty=True).first()
      if bounty:
        issue['is_bounty'] = True
        issue['bounty_amount'] = bounty.amount
    return jsonify(issues), 200

  return jsonify(msg='An error occured fetching issues'), 400