#!/usr/bin/env python3
"""
测试翻译器修复效果
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translator import Translator
from translator_optimized import OptimizedTranslator

def test_simple_translation():
    """测试Simple翻译"""
    print("🧪 测试Simple翻译...")
    
    # 测试原版翻译器
    try:
        translator = Translator("simple")
        result = translator.translate_text("hello world", "zh")
        print(f"✅ 原版Simple翻译: hello world -> {result}")
    except Exception as e:
        print(f"❌ 原版Simple翻译失败: {e}")
    
    # 测试优化版翻译器
    try:
        opt_translator = OptimizedTranslator("simple")
        result = opt_translator.translate_text_cached("hello world", "zh")
        print(f"✅ 优化版Simple翻译: hello world -> {result}")
    except Exception as e:
        print(f"❌ 优化版Simple翻译失败: {e}")

def test_google_translation():
    """测试Google翻译"""
    print("\n🧪 测试Google翻译...")
    
    # 测试原版翻译器
    try:
        translator = Translator("google")
        result = translator.translate_text("hello", "zh")
        print(f"✅ 原版Google翻译: hello -> {result}")
    except Exception as e:
        print(f"❌ 原版Google翻译失败: {e}")
    
    # 测试优化版翻译器
    try:
        opt_translator = OptimizedTranslator("google")
        result = opt_translator.translate_text_cached("hello", "zh")
        print(f"✅ 优化版Google翻译: hello -> {result}")
    except Exception as e:
        print(f"❌ 优化版Google翻译失败: {e}")

def test_language_code_normalization():
    """测试语言代码标准化"""
    print("\n🧪 测试语言代码标准化...")
    
    # 测试优化版翻译器的语言代码映射
    try:
        opt_translator = OptimizedTranslator("google")
        
        test_codes = ['zh', 'zh-CN', 'chinese', 'en', 'english']
        for code in test_codes:
            normalized = opt_translator._normalize_language_code_for_google(code)
            print(f"✅ 语言代码映射: {code} -> {normalized}")
    except Exception as e:
        print(f"❌ 语言代码标准化失败: {e}")

if __name__ == "__main__":
    print("🔧 翻译器修复测试")
    print("=" * 50)
    
    test_simple_translation()
    test_google_translation()
    test_language_code_normalization()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成") 