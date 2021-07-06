BountyHunt API

## Required environment variables
```
FLASK_APP = BountyHunt
BH_SECRET_KEY
BH_SECURITY_PASSWORD_SALT
JWT_SECRET_KEY
DATABASE_URL
```

## Project Setup
```
pip3 nstall -e .
```

## Runs development server
```
flask run
```

## Instructions for migrating database
1. Initiate database migration repo
```
python3 migrate.py db init
```

2. Generate initial migration
```
python3 migrate.py db migrate -m "Initial Migration."
```

3. Apply migration to database
```
python3 migrate.py db upgrade
```