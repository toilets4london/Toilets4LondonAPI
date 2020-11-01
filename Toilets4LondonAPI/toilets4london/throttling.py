from rest_framework import throttling


class PostAnonymousRateThrottle(throttling.AnonRateThrottle):
    scope = 'post_anon'

    def allow_request(self, request, view):
        if request.method == "GET":
            return True
        return super().allow_request(request, view)


class GetAnonymousRateThrottle(throttling.AnonRateThrottle):
    scope = 'get_anon'

    def allow_request(self, request, view):
        if request.method == "POST":
            return True
        return super().allow_request(request, view)
