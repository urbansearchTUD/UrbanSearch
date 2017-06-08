from functools import wraps
from flask import jsonify, request

def is_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify(error=True,
                           status=400,
                           message='Content-Type should be application/json')
        return f(*args, **kwargs)

    return decorated_function
