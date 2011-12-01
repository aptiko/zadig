from functools import wraps
from django.http import HttpResponseNotAllowed
import django.http

from zadig.core.utils import get_request

def require_POST(f):
    @wraps(f)
    def wrapper(*args, **kargs):
        request = get_request()
        if request.method != 'POST':
            r = HttpResponseNotAllowed(['POST'])
            r.write(u'<html><head><title>Not allowed</title></head>'
                    '<body><h1>Not allowed</h1><p>Method not allowed. The most '
                    'common cause for this is that you sent a GET request '
                    'when only a POST is allowed.</p></body></html>')
            return r
        return f(*args, **kargs)
    return wrapper
