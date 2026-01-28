@echo off
REM ===================================================================
REM 前端 Docker 快速启动脚本 (Windows)
REM ===================================================================

setlocal enabledelayedexpansion

REM 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM 打印带颜色的消息
:print_info
echo %GREEN%[INFO]%NC% %~1
goto :eof

:print_warn
echo %YELLOW%[WARN]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查 Docker 是否安装
:check_docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker 未安装，请先安装 Docker"
    exit /b 1
)
call :print_info "Docker 已安装"
goto :eof

REM 检查 Docker Compose 是否安装
:check_docker_compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker Compose 未安装，请先安装 Docker Compose"
    exit /b 1
)
call :print_info "Docker Compose 已安装"
goto :eof

REM 检查后端网络
:check_backend_network
set NETWORK=%~1
docker network inspect %NETWORK% >nul 2>&1
if %errorlevel% neq 0 (
    call :print_warn "后端网络 %NETWORK% 不存在"
    set /p CREATE="是否创建网络? (y/n): "
    if /i "!CREATE!"=="y" (
        docker network create %NETWORK%
        call :print_info "网络 %NETWORK% 创建成功"
    ) else (
        call :print_error "无法启动，需要后端网络"
        exit /b 1
    )
) else (
    call :print_info "后端网络 %NETWORK% 已存在"
)
goto :eof

REM 启动开发环境
:start_dev
call :print_info "启动开发环境..."
call :check_backend_network py-small-admin-network
docker-compose up -d
if %errorlevel% equ 0 (
    call :print_info "开发环境启动成功"
    call :print_info "访问地址: http://localhost:8000"
) else (
    call :print_error "启动失败"
    exit /b 1
)
goto :eof

REM 启动生产环境
:start_prod
call :print_info "启动生产环境..."

REM 检查环境变量文件
if not exist .env.production (
    call :print_warn ".env.production 文件不存在"
    if exist .env.production.example (
        set /p CREATE="是否从 .env.production.example 创建? (y/n): "
        if /i "!CREATE!"=="y" (
            copy .env.production.example .env.production
            call :print_warn "请编辑 .env.production 文件配置环境变量"
            pause
        ) else (
            call :print_error "无法启动，需要 .env.production 文件"
            exit /b 1
        )
    ) else (
        call :print_error "无法启动，需要 .env.production 文件"
        exit /b 1
    )
)

call :check_backend_network py-small-admin-network-prod
docker-compose -f docker-compose.prod.yml up -d --build
if %errorlevel% equ 0 (
    call :print_info "生产环境启动成功"
    call :print_info "访问地址: http://localhost:80"
) else (
    call :print_error "启动失败"
    exit /b 1
)
goto :eof

REM 停止服务
:stop
set ENV=%~1
if "%ENV%"=="prod" (
    call :print_info "停止生产环境..."
    docker-compose -f docker-compose.prod.yml down
) else (
    call :print_info "停止开发环境..."
    docker-compose down
)
call :print_info "服务已停止"
goto :eof

REM 查看日志
:logs
set ENV=%~1
if "%ENV%"=="prod" (
    docker-compose -f docker-compose.prod.yml logs -f
) else (
    docker-compose logs -f
)
goto :eof

REM 重新构建
:rebuild
set ENV=%~1
if "%ENV%"=="prod" (
    call :print_info "重新构建生产环境..."
    docker-compose -f docker-compose.prod.yml build --no-cache
) else (
    call :print_info "重新构建开发环境..."
    docker-compose build --no-cache
)
call :print_info "构建完成"
goto :eof

REM 显示帮助信息
:show_help
echo 用法: %~nx0 [命令] [环境]
echo.
echo 命令:
echo   start     启动服务
echo   stop      停止服务
echo   restart   重启服务
echo   logs      查看日志
echo   rebuild   重新构建镜像
echo   help      显示帮助信息
echo.
echo 环境:
echo   dev       开发环境 (默认)
echo   prod      生产环境
echo.
echo 示例:
echo   %~nx0 start dev      # 启动开发环境
echo   %~nx0 start prod     # 启动生产环境
echo   %~nx0 stop dev       # 停止开发环境
echo   %~nx0 logs dev       # 查看开发环境日志
goto :eof

REM 主函数
:main
call :check_docker
if %errorlevel% neq 0 exit /b %errorlevel%

call :check_docker_compose
if %errorlevel% neq 0 exit /b %errorlevel%

set COMMAND=%~1
if "%COMMAND%"=="" set COMMAND=help
set ENV=%~2
if "%ENV%"=="" set ENV=dev

if "%COMMAND%"=="start" (
    if "%ENV%"=="prod" (
        call :start_prod
    ) else (
        call :start_dev
    )
) else if "%COMMAND%"=="stop" (
    call :stop %ENV%
) else if "%COMMAND%"=="restart" (
    call :stop %ENV%
    if "%ENV%"=="prod" (
        call :start_prod
    ) else (
        call :start_dev
    )
) else if "%COMMAND%"=="logs" (
    call :logs %ENV%
) else if "%COMMAND%"=="rebuild" (
    call :rebuild %ENV%
) else if "%COMMAND%"=="help" (
    call :show_help
) else (
    call :print_error "未知命令: %COMMAND%"
    call :show_help
    exit /b 1
)

goto :eof

REM 执行主函数
call :main %*
