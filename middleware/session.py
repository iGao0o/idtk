from django.core.cache import cache
from importlib import import_module
from django.utils.deprecation import MiddlewareMixin

class TokenMiddleware(MiddlewareMixin):


    def process_request(self, request):
        token = request.headers.get("token")
        if token is not None:
            cache.expire("user:token:%s" % token, timeout=5 * 60)

    def process_response(self, request, response):
        return response
