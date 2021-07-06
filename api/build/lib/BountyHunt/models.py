from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, MetaData
from datetime import datetime
from werkzeug.security import check_password_hash
from sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata, model_class=FlaskBaseModel)
db = initialize_flask_sqlathanor(db)

class User(db.Model):
  user_id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  username = db.Column(db.String, nullable=False, unique=True, supports_dict=True)
  password = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True, supports_dict=True)
  created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), supports_dict=True)
  github_access_token = db.Column(db.String, unique=True, supports_dict=True)
  bounties = db.relationship('Bounty', backref=db.backref('user', lazy='subquery'), lazy=True, foreign_keys='Bounty.user_id', supports_dict=True)
  assigned_bounties = db.relationship('Bounty', lazy=True, foreign_keys='Bounty.assigned_user_id', supports_dict=True)
  applications = db.relationship('BountyApplication', backref='user', lazy=True, supports_dict=True)
  investments = db.relationship('Investment', backref='user', lazy=True, supports_dict=True)
  repos = db.relationship('GithubRepository', backref='user', lazy=True, supports_dict=True)

  def add(self):
    db.session.add(self)
    db.session.commit()

  @classmethod
  def authenticate(cls, username, password):
    if not username or not password:
      return None
    
    user = cls.query.filter(or_(cls.email == username, cls.username == username)).first()
    if not user or not check_password_hash(user.password, password):
      return None

    return user

  def add_github_token(self, token):
    self.github_access_token = token
    db.session.commit()


class Currency(db.Model):
  currency_code = db.Column(db.String, primary_key=True, supports_dict=True)
  name = db.Column(db.String, nullable=False, supports_dict=True)
  symbol = db.Column(db.String, nullable=False, supports_dict=True)

bounty_categories = db.Table('bounty_categories',
  db.Column('bounty_id', db.Integer, db.ForeignKey('bounty.bounty_id', ondelete='CASCADE'), primary_key=True),
  db.Column('category_id', db.Integer, db.ForeignKey('category.category_id', ondelete='CASCADE'), primary_key=True)
)
class Bounty(db.Model):
  bounty_id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  title = db.Column(db.String, nullable=False, supports_dict=True)
  description = db.Column(db.String, supports_dict=True)
  amount = db.Column(db.BigInteger, nullable=False, supports_dict=True)
  allow_multiple_investors = db.Column(db.Boolean, nullable=False, supports_dict=True)
  external_links = db.Column(db.ARRAY(db.String), supports_dict=True)
  created = db.Column(db.DateTime, nullable=False, supports_dict=True)
  last_edited = db.Column(db.DateTime, nullable=False, supports_dict=True)
  url = db.Column(db.String, nullable=False, unique=True, supports_dict=True)
  completed = db.Column(db.Boolean, default=False, supports_dict=True)
  completion_datetime = db.Column(db.DateTime, supports_dict=True)
  is_submit = db.Column(db.Boolean, default=False, supports_dict=True)
  submission_description = db.Column(db.String(1000), supports_dict=True)
  submission_link = db.Column(db.String, supports_dict=True)
  submission_datetime = db.Column(db.DateTime, supports_dict=True)
  currency_code = db.Column(db.String, db.ForeignKey('currency.currency_code', ondelete='NO ACTION'), supports_dict=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), supports_dict=True)
  assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='SET NULL'), supports_dict=True)
  is_git_bounty = db.Column(db.Boolean, default=False, supports_dict=True)
  git_url = db.Column(db.String, unique=True, supports_dict=True)
  categories = db.relationship('Category', secondary=bounty_categories, lazy=True, backref=db.backref('bounties', lazy='subquery'), supports_dict=True)
  applications = db.relationship('BountyApplication', backref='bounty', lazy=True, supports_dict=True)
  investments = db.relationship('Investment', backref='bounty', lazy=True, supports_dict=True)

  def add(self):
    db.session.add(self)
    db.session.commit()

  def assign(self, user_id):
    self.assigned_user_id = user_id
    db.session.commit()

  def update_bounty_amount(self, amount):
    self.amount = self.amount + amount
    db.session.commit()

  def submit(self, description, link):
    self.is_submit = True
    self.submission_description = description
    self.submission_link = link
    self.submission_datetime = datetime.utcnow()
    db.session.commit()

  def complete(self, completion_datetime):
    self.completed = True
    self.completion_datetime = completion_datetime
    db.session.commit()

class Category(db.Model):
  category_id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  name = db.Column(db.String, nullable=False, unique=True, supports_dict=True)

class BountyApplication(db.Model):
  application_id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  application_text = db.Column(db.String, nullable=True, supports_dict=True)
  created = db.Column(db.DateTime, nullable=False, supports_dict=True)
  bounty_id = db.Column(db.Integer, db.ForeignKey('bounty.bounty_id', ondelete='SET NULL'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'))

  def add(self):
    db.session.add(self)
    db.session.commit()
class Investment(db.Model):
  investment_id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  created = db.Column(db.DateTime, nullable=False, supports_dict=True)
  amount = db.Column(db.BigInteger, nullable=False, supports_dict=True)
  currency_code = db.Column(db.String, db.ForeignKey('currency.currency_code', ondelete='NO ACTION'), supports_dict=True)
  bounty_id = db.Column(db.Integer, db.ForeignKey('bounty.bounty_id', ondelete='SET NULL'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'))

  def add(self):
    db.session.add(self)
    db.session.commit()

class BountySubmissionApproval(db.Model):
  bounty_id = db.Column(db.Integer, db.ForeignKey('bounty.bounty_id', ondelete='CASCADE'), primary_key=True, supports_dict=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), primary_key=True, supports_dict=True)
  is_approved = db.Column(db.Boolean, nullable=False, supports_dict=True)
  decision_datetime = db.Column(db.DateTime, nullable=False, supports_dict=True)

  def add(self):
    db.session.add(self)
    db.session.commit()

class GithubRepository(db.Model):
  id = db.Column(db.Integer, primary_key=True, supports_dict=True)
  full_name = db.Column(db.String, unique=True, nullable=False, supports_dict=True)
  html_url = db.Column(db.String, unique=True, nullable=False, supports_dict=True)
  url = db.Column(db.String, unique=True, nullable=False, supports_dict=True)
  description = db.Column(db.String, supports_dict=True)
  owner_avatar_url = db.Column(db.String, nullable=False, supports_dict=True)
  language = db.Column(db.String, supports_dict=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='NO ACTION'), supports_dict=True)

  @classmethod
  def add_repos(cls, repos, user_id):
    for repo in repos:
      new_repo = cls(
        full_name=repo['full_name'],
        html_url=repo['html_url'],
        url=repo['url'],
        description=repo['description'],
        owner_avatar_url=repo['owner']['avatar_url'],
        language=repo['language'],
        user_id=user_id
      )
      db.session.add(new_repo)
    db.session.commit()