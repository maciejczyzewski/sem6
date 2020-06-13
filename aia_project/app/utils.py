from functools import wraps
from flask import request, redirect
from flask import current_app as app_cls
import app.action.user

from webargs import fields, validate
from webargs.flaskparser import parser

FORM_USER_VALID = {
    'name': fields.Str(validate=validate.Length(min=6), required=True),
    'email': fields.Email(required=True),
    'password': fields.Str(validate=validate.Length(min=6), required=True),
}

FORM_TOURNAMENT_VALID = {
    'title': fields.Str(validate=validate.Length(min=6), required=True),
    'max_users': fields.Int(missing=16),
    'location': fields.Str(required=False),
    'readme': fields.Str(required=False),
    'date_start': fields.DateTime(),
    'date_deadline': fields.DateTime(),
    'rating': fields.Int(required=True),
    'license': fields.Str(required=True),
    'score_1': fields.Int(required=True),
    'score_2': fields.Int(required=True),
}

@parser.location_loader("form")
def load_data(request, schema):
    return request.form


class DataError(Exception):
    pass


@parser.error_handler
def handle_error(error, req, schema, *, error_status_code, error_headers):
    raise DataError(error.messages)

################################################################################

def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print("[AUTH]")
            auth_token = request.cookies.get('auth_token')
            app.action.user.user_instance_from_token(app_cls, auth_token)
        except:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def is_anonymous(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print("[AUTH]")
            auth_token = request.cookies.get('auth_token')
            app.action.user.user_instance_from_token(app_cls, auth_token)
            return redirect('/')
        except:
            pass
        return f(*args, **kwargs)
    return decorated_function

