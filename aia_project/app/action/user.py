print("[CORE]")

import random
import datetime
from app.models import User
from pprint import pprint

class ErrFatal(Exception):
    pass


class ErrDuplicate(Exception):
    pass


class ErrWrongPassword(Exception):
    pass


class ErrWrongRecovery(Exception):
    pass


class ErrAuthNotExists(Exception):
    pass


class ErrNotVerified(Exception):
    pass


class ErrTimeout(Exception):
    pass


def user_create(s, data):
    try:
        new_recovery = str(random.random())

        user = User(email=data['email'],
                    name=data['name'],
                    recovery=new_recovery)
        user.hash_password(data['password'])

        s.db.session.add(user)
        s.db.session.commit()
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise ErrDuplicate()
        raise ErrFatal()
    return user


def user_get_auth_token(s, data):
    user = (User.query.filter(User.email == data['email']).first())
    if user is None:
        raise ErrFatal()
    if not user or not user.verify_password(data['password']):
        raise ErrWrongPassword()
    if user.verified is False:
        raise ErrNotVerified()
    return user.generate_auth_token().decode("ascii")


def user_instance_from_token(s, auth_token):
    user = User.verify_auth_token(auth_token)
    if user is None:
        raise ErrAuthNotExists()
    if user.verified is False:
        raise ErrNotVerified()
    return user


def user_new_recovery(s, data):
    user = (User.query.filter(User.email == data['email']).first())
    if user is None:
        raise ErrFatal()
    user.recovery = str(random.random())
    user.date_created = datetime.datetime.utcnow()
    s.db.session.commit()
    return user


def user_try_verify(s, data):
    user = (User.query.filter(User.email == data['email']).first())
    if user is None:
        raise ErrFatal()
    now = datetime.datetime.utcnow()
    if not (now - datetime.timedelta(hours=24) <= user.date_created <= now):
        raise ErrTimeout()
    print(f"user.recovery=|{user.recovery}| ?=|{data['recovery']}|")
    if str(user.recovery) != str(data['recovery']):
        raise ErrWrongRecovery()
    user.verified = True
    s.db.session.commit()


def user_try_forget(s, data):
    user = (User.query.filter(User.email == data['email']).first())
    if user is None:
        raise ErrFatal()
    now = datetime.datetime.utcnow()
    if not (now - datetime.timedelta(hours=24) <= user.date_created <= now):
        raise ErrTimeout()
    print(f"user.recovery=|{user.recovery}| ?=|{data['recovery']}|")
    if str(user.recovery) != str(data['recovery']):
        raise ErrWrongRecovery()
    user.hash_password(data['password'])
    s.db.session.commit()
