"""
HTTP 状态码常量定义

提供标准化的 HTTP 状态码常量，避免在代码中使用魔法数字。
提高代码可读性和维护性。
"""


class StatusCodes:
    """HTTP 状态码常量类"""

    # 成功响应 2xx
    OK = 200  # 请求成功
    CREATED = 201  # 资源创建成功
    ACCEPTED = 202  # 请求已接受，但尚未处理
    NO_CONTENT = 204  # 请求成功，无返回内容
    PARTIAL_CONTENT = 206  # 部分内容

    # 重定向 3xx
    MOVED_PERMANENTLY = 301  # 永久重定向
    FOUND = 302  # 临时重定向
    NOT_MODIFIED = 304  # 资源未修改

    # 客户端错误 4xx
    BAD_REQUEST = 400  # 请求参数错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    METHOD_NOT_ALLOWED = 405  # 方法不允许
    NOT_ACCEPTABLE = 406  # 不可接受
    REQUEST_TIMEOUT = 408  # 请求超时
    CONFLICT = 409  # 资源冲突
    GONE = 410  # 资源已永久删除
    PAYLOAD_TOO_LARGE = 413  # 请求体过大
    UNSUPPORTED_MEDIA_TYPE = 415  # 不支持的媒体类型
    TOO_MANY_REQUESTS = 429  # 请求过多

    # 服务器错误 5xx
    INTERNAL_SERVER_ERROR = 500  # 服务器内部错误
    NOT_IMPLEMENTED = 501  # 功能未实现
    BAD_GATEWAY = 502  # 网关错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用
    GATEWAY_TIMEOUT = 504  # 网关超时
    HTTP_VERSION_NOT_SUPPORTED = 505  # HTTP 版本不支持

    @classmethod
    def is_success(cls, code: int) -> bool:
        """
        判断状态码是否为成功状态 (2xx)

        Args:
            code: HTTP 状态码

        Returns:
            bool: 是否为成功状态
        """
        return 200 <= code < 300

    @classmethod
    def is_client_error(cls, code: int) -> bool:
        """
        判断状态码是否为客户端错误 (4xx)

        Args:
            code: HTTP 状态码

        Returns:
            bool: 是否为客户端错误
        """
        return 400 <= code < 500

    @classmethod
    def is_server_error(cls, code: int) -> bool:
        """
        判断状态码是否为服务器错误 (5xx)

        Args:
            code: HTTP 状态码

        Returns:
            bool: 是否为服务器错误
        """
        return 500 <= code < 600

    @classmethod
    def get_category(cls, code: int) -> str:
        """
        获取状态码分类

        Args:
            code: HTTP 状态码

        Returns:
            str: 状态码分类 (success/client_error/server_error/other)
        """
        if cls.is_success(code):
            return "success"
        elif cls.is_client_error(code):
            return "client_error"
        elif cls.is_server_error(code):
            return "server_error"
        else:
            return "other"


class StatusMessage:
    """响应消息常量类，用于存储增删改查的响应文案"""

    # 创建操作消息
    CREATE_SUCCESS = "创建成功"
    CREATE_FAILED = "创建失败"
    CREATE_ERROR = "创建错误"

    # 查询操作消息
    GET_SUCCESS = "获取成功"
    GET_FAILED = "获取失败"
    GET_ERROR = "获取错误"
    GET_LIST_SUCCESS = "获取列表成功"
    GET_LIST_FAILED = "获取列表失败"
    NOT_FOUND = "资源不存在"

    # 更新操作消息
    UPDATE_SUCCESS = "更新成功"
    UPDATE_FAILED = "更新失败"
    UPDATE_ERROR = "更新错误"

    # 删除操作消息
    DELETE_SUCCESS = "删除成功"
    DELETE_FAILED = "删除失败"
    DELETE_ERROR = "删除错误"
    BATCH_DELETE_SUCCESS = "批量删除成功"
    BATCH_DELETE_FAILED = "批量删除失败"

    # 通用操作消息
    OPERATION_SUCCESS = "操作成功"
    OPERATION_FAILED = "操作失败"
    OPERATION_ERROR = "操作错误"
    SAVE_SUCCESS = "保存成功"
    SAVE_FAILED = "保存失败"

    # 验证相关消息
    VALIDATION_ERROR = "数据验证失败"
    PARAM_ERROR = "参数错误"
    MISSING_REQUIRED_PARAM = "缺少必需参数"
    INVALID_FORMAT = "格式不正确"

    # 权限相关消息
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    TOKEN_EXPIRED = "令牌已过期"
    TOKEN_INVALID = "令牌无效"

    # 系统相关消息
    SERVER_ERROR = "服务器内部错误"
    SYSTEM_BUSY = "系统繁忙，请稍后再试"
    NETWORK_ERROR = "网络错误"
    TIMEOUT = "请求超时"

    @classmethod
    def get_create_message(cls, success: bool = True) -> str:
        """获取创建操作消息"""
        return cls.CREATE_SUCCESS if success else cls.CREATE_FAILED

    @classmethod
    def get_get_message(cls, success: bool = True, is_list: bool = False) -> str:
        """获取查询操作消息"""
        if success:
            return cls.GET_LIST_SUCCESS if is_list else cls.GET_SUCCESS
        else:
            return cls.GET_LIST_FAILED if is_list else cls.GET_FAILED

    @classmethod
    def get_update_message(cls, success: bool = True) -> str:
        """获取更新操作消息"""
        return cls.UPDATE_SUCCESS if success else cls.UPDATE_FAILED

    @classmethod
    def get_delete_message(cls, success: bool = True, is_batch: bool = False) -> str:
        """获取删除操作消息"""
        if success:
            return cls.BATCH_DELETE_SUCCESS if is_batch else cls.DELETE_SUCCESS
        else:
            return cls.BATCH_DELETE_FAILED if is_batch else cls.DELETE_FAILED

    @classmethod
    def get_operation_message(cls, success: bool = True) -> str:
        """获取通用操作消息"""
        return cls.OPERATION_SUCCESS if success else cls.OPERATION_FAILED
