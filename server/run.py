# Windows 系统下使用 SelectorEventLoop 以支持 Playwright 子进程
# 修复 NotImplementedError: ProactorEventLoop 不支持创建子进程
# 必须在所有 import 之前设置，确保 uvicorn 启动时使用正确的事件循环策略
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
