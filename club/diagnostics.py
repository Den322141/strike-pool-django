import logging


logger = logging.getLogger(__name__)


class OutcomeLog:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        level = logging.ERROR if response.status_code >= 500 else logging.WARNING if response.status_code >= 400 else logging.DEBUG
        route = getattr(request.resolver_match, "view_name", None) or "unknown"
        logger.log(level, "%s %s HTTP %s", request.method, route, response.status_code)
        return response
