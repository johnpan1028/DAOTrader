@echo off
chcp 65001
echo 启动 VegaTrader 前端应用...
cd frontend

REM 检查node_modules目录是否存在
echo 检查Node.js依赖...
if not exist "node_modules" (
    echo node_modules目录不存在，开始安装依赖...
    npm install
) else (
    echo 依赖已安装，跳过安装步骤
)

echo 启动Vue开发服务器...
npm run dev
pause







