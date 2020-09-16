

def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    :token  返回的jwt
    :user   当前登录的用户信息[对象]
    :request 当前本次客户端提交过来的数据
    """
    if user.username != None:
        return {
            'code': "fail",
            "status": 200,
            "data": {
                "gcode" : user.username,
                "detail": "请输入验证码,重新登录!",
            }
        }

    return {
        'code': "success",
        "status": 200,
        "data": {
            'token': token,
            'pro_id': user.pro_id,
            'username': user.pro_name,
            'email': user.email,
            'tel_no': user.tel_no,
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

def jwt_response_payload_frequently_error_handler(request = None):
    return {
        "code": "fail",
        "status": 400,
        "data": {
            "detail": "登录失败! 登录频繁! ",
        }
    }

