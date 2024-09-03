from functools import wraps
from flask import request, jsonify, current_app
import jwt
from .models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(identity=data['id']).first()
            print('token_required:current_user', current_user)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired!', 'code': 401, 'extra_code': 2}
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid!', 'code': 401, 'extra_code': 1}
        except Exception as e:
            print('token_required:exception', e)
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated