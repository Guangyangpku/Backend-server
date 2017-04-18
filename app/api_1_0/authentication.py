from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden
from .. import db
from ..email import send_email

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})

#usage:
#http --auth : --json POST http://127.0.0.1:5000/api/v1.0/register/ email=? name=? password=?
@api.route('/register/', methods=['POST'])
def register():
    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')

    if User.query.filter_by(email=email).first(): return jsonify({'status': 'email'})
    elif User.query.filter_by(username=name).first(): return jsonify({'status': 'name'})
    else:
        user = User(email=email,
                    username=name,
                    password=password)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        return jsonify({'status': 'pass'})

@api.route('/login/', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.json.get('email')).first()
    if user is not None and user.verify_password(request.json.get('password')):
        return jsonify({'status': 'pass'})
    return jsonify({'status': 'fail'})
