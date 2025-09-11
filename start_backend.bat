@echo off
chcp 65001
echo 启动 VegaTrader 后端服务...
cd backend

REM 检查是否已安装依赖
echo 检查Python依赖...
python -c "import fastapi, uvicorn, pandas, numpy, talib, akshare, sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo 依赖未完全安装，开始安装...
    pip install -r requirements.txt
) else (
    echo 依赖已安装，跳过安装步骤
)

echo 启动FastAPI服务器...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause



