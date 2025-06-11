@echo off
chcp 65001 >nul
title MCP项目初始化工具

echo.
echo ========================================
echo 🚀 MCP项目初始化工具
echo ========================================
echo.

echo 📦 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python环境正常
echo.

echo 📋 正在检查requirements.txt...
if exist requirements.txt (
    echo ✅ 找到requirements.txt文件
    echo 📦 正在安装依赖包...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ⚠️  未找到requirements.txt文件
    echo 📦 正在安装常用MCP依赖...
    python -m pip install --upgrade pip
    python -m pip install fastmcp pydantic
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
    echo ✅ 基础依赖安装完成
)
echo.

echo 🔧 正在配置MCP设置...
python setup_mcp.py
if errorlevel 1 (
    echo ❌ MCP配置失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 🎉 初始化完成！
echo ========================================
echo.
echo 📝 接下来的步骤:
echo    1. 重启Cursor编辑器
echo    2. 在Cursor中测试MCP工具是否正常工作
echo    3. 开始使用您的MCP项目
echo.
echo 💡 提示: 如果遇到问题，请检查:
echo    - Python版本是否为3.8+
echo    - 网络连接是否正常
echo    - 防火墙是否阻止了Python
echo.

pause 