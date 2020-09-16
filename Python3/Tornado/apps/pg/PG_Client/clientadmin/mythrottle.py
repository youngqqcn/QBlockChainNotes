from rest_framework.throttling import AnonRateThrottle

#登录之前
class LoginBeforeThrottle(AnonRateThrottle):
    scope = 'login_before'
