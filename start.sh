#!/bin/bash

# 工业 Agent 平台启动脚本

echo "=========================================="
echo "   行业智能通用运维模型2.0 启动脚本"
echo "=========================================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误: 未找到 app.py，请在项目根目录运行此脚本"
    exit 1
fi

echo "✓ 项目文件完整"

# 检查依赖是否安装
echo ""
echo "检查 Python 依赖..."

if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Flask 未安装，正在安装依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请手动运行: pip install -r requirements.txt"
        exit 1
    fi
    echo "✓ 依赖安装完成"
else
    echo "✓ 依赖已安装"
fi

# 创建必要的目录
echo ""
echo "创建必要的目录..."
mkdir -p config uploads static
echo "✓ 目录创建完成"

# 启动服务
echo ""
echo "=========================================="
echo "   启动服务中..."
echo "=========================================="
echo ""
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py

