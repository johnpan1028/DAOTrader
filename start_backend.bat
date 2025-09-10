@echo off
echo 启动 VegaTrader 后端服务...
cd backend
echo 安装Python依赖...
pip install -r requirements.txt
echo 启动FastAPI服务器...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause



