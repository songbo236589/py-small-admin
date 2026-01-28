# Python 环境配置完整指南

## 概述

本文档提供了完整的 Python 虚拟环境配置步骤，包括创建、激活、安装依赖和验证的全过程。

## 前置条件

- 已安装 Python 3.12.7 或更高版本
- 已安装 VSCode 并安装 Python 扩展
- 确保在项目根目录 `d:\python\project\quantify001\server` 下执行所有命令
- 如果没有安装Python 3.12.7 请执行以下命令

```cmd
# 清理缓存（损坏的包、临时文件）
conda clean -y --all
# 手动删除锁文件（Windows专属，复制到终端执行）
rd /s /q "C:\Users\tqy63\.conda\locks"
md "C:\Users\tqy63\.conda\locks"

# 重置conda源并重新配置清华镜像（确保下载不卡）
conda config --remove-key channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2/
conda config --set channel_priority strict
conda config --set show_channel_urls yes
# 检查频道配置（确认是清华镜像）
conda config --show channels
conda create -n temp312 python=3.12.7 -y
conda activate temp312
python --version
```
## 这个是关闭所有python应用

```cmd
taskkill /f /im python.exe
```

## 完整配置步骤

### 步骤 1: 创建虚拟环境

如果项目中还没有虚拟环境，请执行以下命令创建：

```cmd
python -m venv venv
```

**验证虚拟环境创建成功**：

```cmd
dir venv
```

应该看到以下输出：

```
2025/12/10  10:16    <DIR>          .
2025/12/10  10:16    <DIR>          ..
2025/12/10  10:16    <DIR>          Include
2025/12/10  10:16    <DIR>          Lib
2025/12/10  10:16               236 pyvenv.cfg
2025/12/10  10:16    <DIR>          Scripts
```

### 步骤 2: 激活虚拟环境

根据您使用的终端类型，选择对应的命令：

#### 方式 A: 使用命令提示符 (CMD) - 推荐

```cmd
venv\Scripts\activate
```

#### 方式 B: 使用 PowerShell

如果遇到执行策略问题，请先执行以下命令（临时允许脚本执行）：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

然后激活虚拟环境（推荐使用批处理文件）：

```powershell
venv\Scripts\activate.bat
或
.\venv\Scripts\Activate.ps1   建议
```

#### 方式 C: 使用 Git Bash 或其他 Unix-like 终端

```bash
source venv/Scripts/activate
```

**验证激活成功**：
激活成功后，命令行前面会显示 `(venv)` 前缀，例如：

```cmd
(venv) PS D:\python\project\quantify001\server>
```

### 步骤 3: 升级 pip

激活虚拟环境后，首先升级 pip 到最新版本：

```cmd
python -m pip install --upgrade pip
```

**验证 pip 升级**：

```cmd
pip --version
```

应该显示最新版本号，例如：

```
pip 25.3.1 from d:\python\project\quantify001\server\venv\lib\site-packages\pip (python 3.11)
```

**清华 PyPI 镜像安装**：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**查看一个包的最新版本**：

```cmd
pip index versions ruff
```

### 步骤 4: 安装项目依赖

安装项目所需的所有依赖包：

```cmd
pip install -r requirements.txt
```

**验证安装**：

```cmd
pip list
```

应该看到安装的包列表，包括但不限于：

- fastapi
- uvicorn
- sqlalchemy
- redis
- pyjwt
- ruff
- 等等

### 步骤 5: 验证环境配置

#### 5.1 验证 Python 解释器

```cmd
python --version
where python
```

应该指向虚拟环境中的 Python，例如：

```
Python 3.12.7
d:\python\project\quantify001\server\venv\Scripts\python.exe
```

#### 5.2 验证代码格式化工具

```cmd
ruff --version

```

应该显示各工具的版本信息。

#### 5.3 测试代码格式化

```cmd
venv\Scripts\ruff.exe check . --fix
```

这些命令应该能够正常运行（可能会有格式化提示，这是正常的）。

## 常见问题解决

### 问题 1: 虚拟环境创建失败

**症状**：执行 `python -m venv venv` 时出现错误

**解决方案**：

1. 确保已安装 Python 并添加到 PATH
2. 检查是否有足够的磁盘空间
3. 尝试使用完整路径：
   ```cmd
   C:\Python311\python.exe -m venv venv
   ```

### 问题 2: PowerShell 激活相关问题

**症状 A：无法识别 Activate.ps1**

```
.\venv\Scripts\Activate.ps1 : The term '.\venv\Scripts\Activate.ps1' is not recognized...
```

**解决方案**：使用批处理文件代替

```powershell
venv\Scripts\activate.bat
```

**症状 B：执行策略限制**

```
无法加载文件...因为在此系统上禁止运行脚本
```

**解决方案**：设置执行策略

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**症状 C：命令执行后没有任何反应**

```
PS D:\python\project\quantify001\server> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
PS D:\python\project\quantify001\server> venv\Scripts\activate.bat
PS D:\python\project\quantify001\server>
```

**分析**：这是正常现象！PowerShell 中的这些命令成功执行时通常不会显示任何输出消息。

**症状 D：验证命令也没有输出**

```
PS D:\python\project\quantify001\server> where python
PS D:\python\project\quantify001\server>
```

**分析**：这表明虚拟环境**未成功激活**。`where python` 应该显示 Python 的路径。

**解决方案**：

#### 方法 1：使用 CMD 而不是 PowerShell（推荐）

1. 打开命令提示符 (CMD) 而不是 PowerShell
2. 在 CMD 中执行：
   ```cmd
   venv\Scripts\activate
   ```
3. 验证激活：
   ```cmd
   where python
   ```

#### 方法 2：在 PowerShell 中使用不同的激活方式

```powershell
# 尝试使用 PowerShell 脚本而不是批处理文件
.\venv\Scripts\Activate.ps1
```

#### 方法 3：手动设置环境变量

```powershell
# 手动添加虚拟环境到 PATH
$env:PATH = "d:\python\project\quantify001\server\venv\Scripts;" + $env:PATH
$env:VIRTUAL_ENV = "d:\python\project\quantify001\server\venv"
```

#### 方法 4：重新创建虚拟环境

```powershell
# 删除现有虚拟环境
Remove-Item -Recurse -Force venv

# 重新创建
python -m venv venv

# 使用 CMD 激活（推荐）
```

**验证成功激活的标志**：
成功激活后，`where python` 应该显示：

```
d:\python\project\quantify001\server\venv\Scripts\python.exe
```

**推荐方案**：在 Windows 上，**强烈建议使用命令提示符 (CMD) 而不是 PowerShell** 来激活 Python 虚拟环境，因为 CMD 对虚拟环境的支持更加稳定和直接。

### 问题 3: pip 安装速度慢或失败

**解决方案 1：使用国内镜像源**

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**解决方案 2：配置永久镜像源**

```cmd
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**解决方案 3：升级 pip 后重试**

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 问题 4: VSCode 无法识别虚拟环境

**解决方案 1：重新加载 VSCode**

1. 按 `Ctrl+Shift+P`
2. 输入 `Developer: Reload Window`
3. 按 Enter 执行

**解决方案 2：手动选择解释器**

1. 按 `Ctrl+Shift+P`
2. 输入 `Python: Select Interpreter`
3. 选择 `./venv/Scripts/python.exe`

**解决方案 3：检查配置文件**
确保 `.vscode/settings.json` 中有正确的配置：

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe"
}
```

### 问题 5: 依赖安装后没有明显变化

**验证步骤**：

1. 检查 pip list 输出：
   ```cmd
   pip list
   ```
2. 检查特定包是否安装：
   ```cmd
   pip show fastapi
   ```
3. 检查虚拟环境大小：
   ```cmd
   dir venv\Lib\site-packages
   ```

## 日常使用指南

### 激活虚拟环境

每次开始开发前，先激活虚拟环境：

```cmd
venv\Scripts\activate
```

### 安装新包

```cmd
pip install package_name
```

### 更新 requirements.txt

```cmd
pip freeze > requirements.txt
```

### 退出虚拟环境

```cmd
deactivate
```

### 代码格式化

```cmd
venv\Scripts\ruff.exe check .
```

## 环境隔离的重要性

使用虚拟环境的好处：

- **依赖隔离**：避免不同项目间的依赖冲突
- **版本控制**：每个项目可以使用不同版本的依赖包
- **部署一致性**：确保开发环境与生产环境一致
- **系统保护**：避免污染系统级的 Python 安装

## 快速参考命令

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (CMD)
venv\Scripts\activate

# 激活虚拟环境 (PowerShell)
venv\Scripts\activate.bat

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 检查安装
pip list

# 退出虚拟环境
deactivate
```

通过以上步骤，您的项目现在拥有了一个完整、独立的 Python 开发环境。
