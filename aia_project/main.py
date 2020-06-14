import unittest
from flask_script import Manager, Command
from test import create_test_suite
from app import Service

service = Service()
service.start()

############################################

"""
from celery import Celery

CELERY_BROKER_BACKEND = "db+sqlite:///celery.sqlite"
CELERY_CACHE_BACKEND = "db+sqlite:///celery.sqlite"
CELERY_RESULT_BACKEND = "db+sqlite:///celery.sqlite"

celery = Celery('tasks', broker='pyamqp://guest@localhost//')
"""

############################################


class CreateCommand(Command):
    "Runs service creator i.e. database"

    def run(self):
        service.db.create_all()
        service.db.session.commit()
        print("[database created]")


class TestCommand(Command):
    "Runs tests (same as `python3 -m unittest`)"

    def run(self):
        testSuite = create_test_suite()
        text_runner = unittest.TextTestRunner(verbosity=2).run(testSuite)


manager = Manager(service.app)
manager.add_command('create', CreateCommand)
manager.add_command('test', TestCommand)

if __name__ == '__main__':
    manager.run()
