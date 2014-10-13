#!/usr/bin/env python
import os
from application import create_app, db
from application.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# create_app defined in app (see imports)
application = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(application)


def make_shell_context():
    return dict(app=application, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))

migrate = Migrate(application, db)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
