# 创建 FastAPI 应用实例，使用配置系统

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from Modules.admin.routes import main_router as admin_router
from Modules.common.libs.app import lifespan
from Modules.common.libs.config import Config, ConfigRegistry
from Modules.common.libs.exception import register_exception_handlers
from Modules.common.libs.responses.response import success
from Modules.content.routes import main_router as content_router
from Modules.quant.routes import main_router as quant_router

# 应用启动时加载一次
ConfigRegistry.load()


app = FastAPI(
    title=Config.get("app.name"),
    description=Config.get("app.description"),
    version=Config.get("app.version"),
    debug=Config.get("app.debug"),
    lifespan=lifespan,
    # 可以根据 docs_enabled 配置控制文档
    docs_url=Config.get("app.docs_url") if Config.get("app.docs_enabled") else None,
    redoc_url=None,  # 也可以控制 ReDoc
    openapi_url=Config.get("app.openapi_url")
    if Config.get("app.docs_enabled")
    else None,
    # 添加安全方案配置
    openapi_components={
        "securitySchemes": {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        }
    },
)


# 读取配置，解决跨域问题
allow_all = Config.get("app.cors_allow_all")
origins = Config.get("app.cors_origins")
methods = Config.get("app.cors_methods")
headers = Config.get("app.cors_headers")

# 如果允许所有来源，直接设置 ["*"]
if allow_all:
    origins = ["*"]

# 添加 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)


# 根路径接口，提供系统信息
@app.get("/", summary="系统信息", tags=["系统"])
async def root():
    """
    获取系统基本信息

    返回系统的基本信息，包括名称、描述、版本等。
    """
    return success(
        {
            "name": Config.get("app.name"),
            "description": Config.get("app.description"),
            "font_size": Config.get("captcha.font_size"),
        },
        message="项目介绍",
    )


# 自定义 OpenAPI 3.0.0 规范接口（仅在 debug 模式下可用）
if Config.get("app.debug"):

    @app.get("/openapi3.json", include_in_schema=False)
    async def get_openapi3_schema():
        """
        获取 OpenAPI 3.0.0 规范的 API 文档

        提供 OpenAPI 3.0.0 版本的 API 规范，用于兼容不支持 3.1.0 的工具
        """
        # 获取原始的 OpenAPI 规范
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # 修改 OpenAPI 版本为 3.0.0
        openapi_schema["openapi"] = "3.0.0"

        return openapi_schema


# 挂载静态文件目录
upload_dir = Config.get("upload.dir", "uploads")
# 检查并创建上传目录
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)

app.mount(
    Config.get("upload.url_prefix", "/uploads"),
    StaticFiles(directory=upload_dir),
    name="uploads",
)

# 注册异常处理器
register_exception_handlers(app)

app.include_router(admin_router, prefix=Config.get("app.api_prefix", ""))
app.include_router(quant_router, prefix=Config.get("app.api_prefix", ""))
app.include_router(content_router, prefix=Config.get("app.api_prefix", ""))
