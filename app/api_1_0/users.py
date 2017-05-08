from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post
from .errors import unauthorized, forbidden

#http --json POST http://127.0.0.1:5000/api/v1.0/users/ email=lzy3qy@gmail.com password=lalala
@api.route('/users/', methods=['POST'])
def getInfo():
    user = User.query.filter_by(email=request.json.get('email')).first()
    if user is not None and user.verify_password(request.json.get('password')):
        return jsonify(user.getInfo())
    else:
        return forbidden('Insufficient permissions')
