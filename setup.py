#!/usr/bin/env python3
"""
CaptionFlow 安装验证脚本
检查依赖安装和环境配置
"""

import sys
import subprocess
import os
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("   需要Python 3.8或更高版本")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True

def check_ffmpeg():
    """检查FFmpeg安装"""
    print("\n🔍 检查FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ FFmpeg未找到")
        print("   请安装FFmpeg: https://ffmpeg.org/download.html")
        return False

def check_package(package_name, display_name=None):
    """检查Python包"""
    if display_name is None:
        display_name = package_name
    
    try:
        importlib.import_module(package_name)
        print(f"✅ {display_name}")
        return True
    except ImportError:
        print(f"❌ {display_name} 未安装")
        return False

def check_python_packages():
    """检查Python依赖包"""
    print("\n🔍 检查Python依赖包...")
    
    packages = [
        ('whisper', 'OpenAI Whisper'),
        ('openai', 'OpenAI'),
        ('moviepy', 'MoviePy'),
        ('srt', 'SRT'),
        ('langdetect', 'Language Detect'),
        ('googletrans', 'Google Translate'),
        ('pysrt', 'PySRT'),
        ('ffmpeg', 'FFmpeg Python'),
        ('streamlit', 'Streamlit'),
        ('dotenv', 'Python Dotenv')
    ]
    
    all_installed = True
    for package, display in packages:
        if not check_package(package, display):
            all_installed = False
    
    return all_installed

def install_packages():
    """安装依赖包"""
    print("\n📦 安装Python依赖包...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        return False

def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境配置...")
    
    # 检查是否有.env文件
    if os.path.exists('.env'):
        print("✅ 找到 .env 配置文件")
    else:
        print("ℹ️  未找到 .env 文件 (可选)")
        if os.path.exists('env.example'):
            print("   可以复制 env.example 为 .env 并配置")
    
    # 检查OpenAI API密钥
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("✅ 找到 OpenAI API密钥")
    else:
        print("ℹ️  未配置 OpenAI API密钥 (使用Google翻译可忽略)")
    
    return True

def create_test_files():
    """创建测试目录"""
    print("\n📁 创建必要目录...")
    
    directories = ['output', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 目录: {directory}/")
    
    return True

def run_basic_test():
    """运行基础测试"""
    print("\n🧪 运行基础功能测试...")
    
    try:
        # 测试导入主要模块
        from caption_generator import CaptionGenerator
        from translator import Translator
        import utils
        
        print("✅ 模块导入测试通过")
        
        # 测试Whisper模型加载（使用最小模型）
        print("🔧 测试Whisper模型加载...")
        try:
            caption_gen = CaptionGenerator(model_size="tiny")
            print("✅ Whisper模型加载成功")
            caption_gen.cleanup()
        except Exception as e:
            print(f"❌ Whisper模型加载失败: {e}")
            return False
        
        # 测试翻译器初始化
        print("🌍 测试翻译器初始化...")
        try:
            translator = Translator(service="google")
            print("✅ Google翻译器初始化成功")
        except Exception as e:
            print(f"❌ 翻译器初始化失败: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🎬 CaptionFlow 环境检查工具")
    print("=" * 50)
    
    all_checks_passed = True
    
    # 检查Python版本
    if not check_python_version():
        all_checks_passed = False
    
    # 检查FFmpeg
    if not check_ffmpeg():
        all_checks_passed = False
    
    # 检查Python包
    if not check_python_packages():
        print("\n❓ 是否要自动安装缺失的依赖包? (y/n): ", end="")
        response = input().strip().lower()
        if response in ['y', 'yes', '是']:
            if install_packages():
                # 重新检查
                if not check_python_packages():
                    all_checks_passed = False
            else:
                all_checks_passed = False
        else:
            all_checks_passed = False
    
    # 检查环境配置
    check_environment()
    
    # 创建必要目录
    create_test_files()
    
    # 运行基础测试
    if all_checks_passed:
        if not run_basic_test():
            all_checks_passed = False
    
    # 输出结果
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 环境检查完成！CaptionFlow已准备就绪")
        print("\n🚀 快速开始:")
        print("   Web界面: streamlit run app.py")
        print("   命令行: python main.py -i your_video.mp4 --bilingual")
    else:
        print("⚠️  环境检查发现问题，请解决上述问题后重新运行")
        print("\n💡 获取帮助:")
        print("   1. 查看 README.md")
        print("   2. 检查依赖安装: pip install -r requirements.txt")
        print("   3. 安装FFmpeg: https://ffmpeg.org/download.html")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 