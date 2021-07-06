#!/usr/bin/env python3
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from BountyHunt import create_app
from BountyHunt.models import db

app = create_app()
db.init_app(app)

migrate = Migrate(app, db, compare_type=True)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()