import jwt
import os
from functools import wraps
from flask import request, jsonify


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401

        try:
            payload = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY'),
                algorithms=['HS256']
            )
            request.usuario_logado = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'erro': 'Token expirado. Faça login novamente.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'erro': 'Token inválido.'}), 401

        return f(*args, **kwargs)
    return decorated