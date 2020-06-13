# http://www.aropupu.fi/bracket/

import base64
from flask import Blueprint
from flask import render_template
from flask import request, redirect
from flask import make_response
from flask import current_app as app_cls
from pprint import pprint

import app.action.user
from app.log import print
from app.utils import is_anonymous, is_authenticated
from app.utils import FORM_USER_VALID, parser, DataError
from app.mail import send_message_verify, send_message_forget

bp = Blueprint('user', __name__)


#####################################################################
@bp.context_processor
def utility_processor():
    def current_user():
        try:
            print("[AUTH]")
            auth_token = request.cookies.get('auth_token')
            return app.action.user.user_instance_from_token(app_cls, auth_token)
        except:
            return None

    return dict(current_user=current_user)


#####################################################################


@bp.route('/signup', methods=['GET', 'POST'])
@is_anonymous
def signup():
    errors = {}
    successes = {}
    FORM_ARGS = {
        'name': FORM_USER_VALID['name'],
        'email': FORM_USER_VALID['email'],
        'password': FORM_USER_VALID['password'],
    }
    if request.method == 'POST':
        print("POST")
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            pprint(parsed_args)
            user = app.action.user.user_create(app_cls.service, parsed_args)
            url = send_message_verify(user.email, user.recovery)
            print(user.recovery)
            successes = {
                "user": [
                    f"We've sent you an email to {user.email} to verify your account. (debug: {url})"
                ]
            }
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except app.action.user.ErrDuplicate as e:
            print("ERROR", "duplicate")
            errors = {"user": ["This user already exists (with this email)."]}
    return render_template('signup.html', errors=errors, successes=successes)


# FIXME: block pages by decorator!
@bp.route('/login', methods=['GET', 'POST'])
@is_anonymous
def login():
    errors = {}
    FORM_ARGS = {
        'email': FORM_USER_VALID['email'],
        'password': FORM_USER_VALID['password'],
    }
    auth_token = None
    if request.method == 'POST':
        print("POST")
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            pprint(parsed_args)
            auth_token = app.action.user.user_get_auth_token(app_cls.service,
                                                      parsed_args)
            #resp.set_cookie('auth_token', auth_token)
            print(f"--> auth_token {auth_token}")
            # FIXME: register auth_token cookie
            # FIXME: redirect
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except app.action.user.ErrWrongPassword as e:
            print("ERROR", "wrong password")
            errors = {"user": ["Wrong password or user does not exists."]}
        except app.action.user.ErrNotVerified as e:
            print("ERROR", "not verified")
            errors = {"user": ["User not verified, please check your email."]}
    resp = make_response(render_template('login.html', errors=errors))
    if auth_token:
        resp = make_response(redirect('/'))
        resp.set_cookie('auth_token', auth_token)
    return resp


@bp.route('/verify/<code>')
@is_anonymous
def verify(code):
    errors = {}
    successes = {}
    args = base64.b64decode(code.encode('utf-8')).decode('utf-8')
    email, recovery = args.split("/")
    print(f"|{email}|, |{recovery}|")
    try:
        app.action.user.user_try_verify(app_cls.service, {
            "email": email,
            "recovery": recovery
        })
        successes = {"user": [f"Account for {email} is now active."]}
    except app.action.user.ErrWrongRecovery as e:
        print("ERROR", "wrong recovery")
        errors = {"user": [f"Wrong recovery code for {email}."]}
    except app.action.user.ErrTimeout as e:
        print("ERROR", "timeout")
        errors = {"user": [f"Timeout (more than 24h) for {email}."]}
    return render_template('verify.html', errors=errors, successes=successes)


@bp.route('/forget', methods=['GET', 'POST'])
@is_anonymous
def forget():
    errors = {}
    successes = {}
    FORM_ARGS = {
        'email': FORM_USER_VALID['email'],
    }
    if request.method == 'POST':
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            pprint(parsed_args)
            user = app.action.user.user_new_recovery(app_cls.service, parsed_args)
            url = send_message_forget(user.email, user.recovery)
            successes = {
                "user": [
                    f"We've sent you an email to {user.email} to recover your account. (debug: {url})"
                ]
            }
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except Exception as e:
            print("HACKER/DDOS?", e)
    return render_template('forget.html', errors=errors, successes=successes)


@bp.route('/forget/<code>', methods=['GET', 'POST'])
@is_anonymous
def forget_code(code):
    errors = {}
    successes = {}
    args = base64.b64decode(code.encode('utf-8')).decode('utf-8')
    email, recovery = args.split("/")
    print(f"|{email}|, |{recovery}|")
    FORM_ARGS = {
        'password': FORM_USER_VALID['password'],
    }
    if request.method == 'POST':
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            pprint(parsed_args)
            app.action.user.user_try_forget(
                app_cls.service, {
                    "email": email,
                    "recovery": recovery,
                    "password": parsed_args["password"]
                })
            successes = {"user": [f"Account for {email} is now active."]}
        except app.action.user.ErrWrongRecovery as e:
            print("ERROR", "wrong recovery")
            errors = {"user": [f"Wrong recovery code for {email}."]}
        except app.action.user.ErrTimeout as e:
            print("ERROR", "timeout")
            errors = {"user": [f"Timeout (more than 24h) for {email}."]}
    return render_template('forget_code.html',
                           email=email,
                           errors=errors,
                           successes=successes)


@bp.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('auth_token', '', expires=0)
    return resp


@bp.route('/profile/<idx>')
def profile(idx):
    from app.models import User
    user = (User.query.filter(User.id == idx).first())

    from app.models import Match
    matches = (Match.query.filter(Match.user_id_1 == idx).all()) + (Match.query.filter(Match.user_id_2 == idx).all())

    tiers = user.tiers

    return render_template('profile.html', user=user, matches=matches,
            tiers=tiers)


@bp.route('/players')
def players():
    from app.models import User
    users = (User.query.filter(User.verified == True).all())
    return render_template('players.html', users=users)
