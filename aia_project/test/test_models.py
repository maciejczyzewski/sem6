import unittest
from app import Service
from config import Config

from app.models import User
from app.log import print
import app.action.user


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.service = Service(TestConfig)
        self.service.start()

    def tearDown(self):
        self.service.end()

    def test_user_created(self):
        user_1 = {
            "email": 'test1@example.com',
            "password": '1234',
            "name": "Test 1"
        }

        user_2 = {
            "email": 'test2@example.com',
            "password": '1234',
            "name": "Test 2"
        }

        app.action.user.user_create(self.service, user_1)
        app.action.user.user_create(self.service, user_2)

        v1 = 0
        print("")
        for user in User.query.all():
            print(f"---> {user} {user.date_created}")
            print(f"\t{user.password_hash}")
            print(f"\tverified={user.verified} token={user.recovery}")
            self.assertEqual(user.verified, False)
            v1 += 1

        self.assertEqual(v1, 2)

    def test_user_created_duplicate(self):
        self.test_user_created()

        user_2 = {
            "email": 'test2@example.com',
            "password": '1234',
            "name": "Test 2"
        }

        with self.assertRaises(app.action.user.ErrDuplicate):
            app.action.user.user_create(self.service, user_2)

    def test_user_auth_token(self):
        self.test_user_created()
        email = "test2@example.com"

        with self.assertRaises(app.action.user.ErrWrongPassword):
            app.action.user.user_get_auth_token(self.service, {
                "email": email,
                "password": "12345"
            })

        # FIXME: now you can't do this!
        auth_token = app.action.user.user_get_auth_token(self.service, {
            "email": email,
            "password": "1234"
        })

        with self.assertRaises(app.action.user.ErrAuthNotExists):
            app.action.user.user_instance_from_token(self.service, auth_token + "x")

        with self.assertRaises(app.action.user.ErrNotVerified):
            app.action.user.user_instance_from_token(self.service, auth_token)

        user = (User.query.filter(User.email == email).first())

        with self.assertRaises(app.action.user.ErrWrongRecovery):
            app.action.user.user_try_verify(self.service, {
                "email": email,
                "recovery": user.recovery + "123"
            })

        app.action.user.user_try_verify(self.service, {
            "email": email,
            "recovery": user.recovery
        })

        print(f"\nauth_token ----> {auth_token}")
        holder = app.action.user.user_instance_from_token(self.service, auth_token)
        self.assertEqual(holder.email, email)

    def test_user_new_recovery(self):
        self.test_user_created()
        email = "test2@example.com"

        user = (User.query.filter(User.email == email).first())
        r_old = user.recovery

        app.action.user.user_new_recovery(self.service, {"email": email})

        user = (User.query.filter(User.email == email).first())
        r_new = user.recovery

        self.assertNotEqual(r_old, r_new)

    def test_user_forget_password(self):
        self.test_user_created()
        email = "test2@example.com"
        new_password = "123456"

        user = (User.query.filter(User.email == email).first())
        app.action.user.user_try_forget(self.service, {
            "email": email,
            "recovery": user.recovery,
            "password": new_password
        })

        with self.assertRaises(app.action.user.ErrWrongPassword):
            app.action.user.user_get_auth_token(self.service, {
                "email": email,
                "password": "1234"
            })

        app.action.user.user_get_auth_token(self.service, {
            "email": email,
            "password": "123456"
        })
