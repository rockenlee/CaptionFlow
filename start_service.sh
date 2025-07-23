#!/bin/bash

echo "🎬 启动 CaptionFlow 服务..."

# 检查虚拟环境是否存在
if [ ! -d "captionflow_env" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 激活虚拟环境
source captionflow_env/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 启动 Streamlit Web 服务..."
    echo "📍 访问地址: http://localhost:8502"
    echo "⌨️  按 Ctrl+C 停止服务"
    echo ""
    
    # 启动Streamlit服务（支持4GB文件上传）
    streamlit run app.py --server.port 8502 --server.maxUploadSize 4096
else
    echo "❌ 依赖检查失败，请检查环境配置"
    exit 1
fi 