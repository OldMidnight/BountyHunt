
#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
  name='BountyHunt',
  version='1.0.0',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=[
      'flask==1.1.2',
      'flask-cors==3.0.10',
      'flask-SQLAlchemy==2.5.1',
      'psycopg2-binary==2.8.6',
      'flask-migrate==2.7.0',
      'flask-script==2.0.6',
      'flask-jwt-extended==4.1.0',
      'sqlathanor==0.7.0',
      'stripe==2.56.0'
  ],
)