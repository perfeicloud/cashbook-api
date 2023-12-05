from flask import jsonify, make_response

def r(code=200, msg:str=None, data=None, token:str=None):
    """返回JSON
    ---

    `code`状态码:
    ::

        200 - (OK) 请求成功，返回响应(GET)
        201 - (Created) 请求资源已创建无需回应(POST)
        202 - (Accepted) 客户端请求正在被执行，但还没有处理完
        204 - (NoContent) 请求成功处理无需回应(PUT/PATCH/DELETE)

        400 - (BadRequest) 客户端错误请求或错误参数
        401 - (Unauthorized) 客户端请求未经授权
        403 - (Forbidden) 客户端已授权，但没有使用资源的权限
        404 - (NotFound) 客户端请求的资源未找到
        405 - (MethodNotAllowed) 请求方法对某些资源不允许使用
        408 - (RequestTimeout) 请求超时
        410 - (Gone) 被请求的资源在服务器上已经永久性的不再可用
        415 - (UnsupportedMediaType) 请求媒体类型服务器不支持
        423 - (Locked) 当前资源被锁定
        429 - (TooManyRequests) 请求次数太多，当需要限制客户端请求数量时

        500 - (InternalServerError) 内部服务器错误
        501 - (NotImplemented) 服务器无法识别请求的方法
        502 - (BadGateway) 错误的网关
        503 - (ServiceUnavailable) 服务器由于在维护或已经超载而无响应
    """
    res = {
        'code': code
    }
    if msg:
        res['msg'] = msg
    if data is not None:
        res['data'] = data

    return make_response(jsonify(res), code)