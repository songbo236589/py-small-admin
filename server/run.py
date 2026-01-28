import uvicorn

from Modules.common.libs.config import Config, ConfigRegistry

# 应用启动时加载一次
ConfigRegistry.load()

if __name__ == "__main__":
    uvicorn.run(
        "Modules.main:app",
        host=Config.get("app.host"),
        port=int(Config.get("app.port")),
        reload=Config.get("app.reload"),
    )
