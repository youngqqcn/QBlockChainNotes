


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    :token  返回的jwt
    :user   当前登录的用户信息[对象]
    :request 当前本次客户端提交过来的数据
    """

    return {
        'code': "success",
        "status": 200,
        "data": {
            'token': token,
            'id': user.id,
            'username': user.username,
            'email': user.email,
            "detail": "登录成功!",
        }
    }

def jwt_response_payload_error_handler(request = None):
    return {
        "code": "fail",
        "status": 400,
        "data": {
            "detail": "登录失败! 请检查账号信息是否正确,重新登录! ",
        }
    }

def jwt_response_payload_code_error_handler(request = None):
    return {
        "code": "fail",
        "status": 400,
        "data": {
            "detail": "登录失败! 请检查谷歌验证码是否正确,重新登录! ",
        }
    }


