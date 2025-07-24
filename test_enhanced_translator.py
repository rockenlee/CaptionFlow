#!/usr/bin/env python3
"""
测试增强版翻译器 - Microsoft Translator API集成
"""

import sys
import os
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translator import Translator
from translator_optimized import OptimizedTranslator
from translator_enhanced import MicrosoftTranslatorEnhanced

def test_enhanced_simple_translation():
    """测试增强版Simple翻译"""
    print("🚀 测试增强版Simple翻译（Microsoft Translator API集成）\n")
    
    # 测试文本
    test_texts = [
        # 基础词汇（本地词典应该能处理）
        "hello",
        "world",
        "thank you", 
        "good morning",
        
        # 复杂句子（需要API处理）
        "This is a complex sentence that requires advanced translation.",
        "Machine learning is revolutionizing the translation industry.", 
        "How does artificial intelligence impact human translators?",
        "The weather is beautiful today, and I'm going for a walk.",
        "Can you help me translate this document into Chinese?",
        "I love programming and building amazing applications."
    ]
    
    print("1️⃣ 测试原版翻译器（增强版Simple）:")
    translator = Translator("simple")
    
    for text in test_texts:
        try:
            start_time = time.time()
            result = translator.translate_text(text, "zh")
            end_time = time.time()
            
            print(f"   📝 {text}")
            print(f"   ➡️  {result}")
            print(f"   ⏱️  {(end_time - start_time)*1000:.1f}ms\n")
            
        except Exception as e:
            print(f"   ❌ 翻译失败: {e}\n")
    
    print("\n" + "="*60 + "\n")
    
    print("2️⃣ 测试优化版翻译器（增强版Simple）:")
    opt_translator = OptimizedTranslator("simple")
    
    print("   📝 单个翻译测试:")
    for text in test_texts[:5]:  # 只测试前5个
        try:
            start_time = time.time()
            result = opt_translator.translate_text_cached(text, "zh")
            end_time = time.time()
            
            print(f"   📝 {text}")
            print(f"   ➡️  {result}")
            print(f"   ⏱️  {(end_time - start_time)*1000:.1f}ms\n")
            
        except Exception as e:
            print(f"   ❌ 翻译失败: {e}\n")
    
    print("\n" + "="*60 + "\n")
    
    print("3️⃣ 直接测试Microsoft Translator增强版:")
    ms_translator = MicrosoftTranslatorEnhanced()
    
    # 测试性能统计
    for text in test_texts[:5]:  # 只测试前5个
        result = ms_translator.translate_text(text, "zh")
        print(f"   📝 {text}")
        print(f"   ➡️  {result}\n")
    
    # 显示性能统计
    stats = ms_translator.get_performance_stats()
    print("   📊 性能统计:")
    for key, value in stats.items():
        print(f"      {key}: {value}")

def test_language_support():
    """测试多语言支持"""
    print("\n\n🌍 测试多语言支持:")
    
    ms_translator = MicrosoftTranslatorEnhanced()
    
    test_phrase = "Hello, how are you?"
    target_languages = ['zh', 'ja', 'ko', 'fr', 'de', 'es', 'ru']
    
    print(f"   原文: {test_phrase}\n")
    
    for lang in target_languages:
        try:
            result = ms_translator.translate_text(test_phrase, lang)
            lang_name = ms_translator.get_language_name(lang)
            print(f"   {lang_name} ({lang}): {result}")
        except Exception as e:
            print(f"   {lang}: ❌ 失败 - {e}")

def test_configuration_guide():
    """测试配置指南"""
    print("\n\n⚙️  配置指南:")
    
    # 检查API密钥
    api_key = os.getenv('AZURE_TRANSLATOR_KEY')
    if api_key:
        print("   ✅ 检测到Azure Translator API密钥")
        print("   🚀 将使用完整Microsoft Translator API功能")
        print(f"   🔑 API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    else:
        print("   ⚠️  未检测到Azure Translator API密钥")
        print("   📝 将使用本地词典 + 回退标记模式")
        print("\n   🔧 如何获取免费API密钥:")
        print("   1. 访问 https://portal.azure.com")
        print("   2. 创建免费Azure账户")
        print("   3. 创建 'Translator' 资源")
        print("   4. 获取API密钥（每月200万字符免费配额）")
        print("   5. 设置环境变量: export AZURE_TRANSLATOR_KEY='your-key-here'")
        print("   6. 或在.env文件中添加: AZURE_TRANSLATOR_KEY=your-key-here")

def test_error_handling():
    """测试错误处理"""
    print("\n\n🛡️ 测试错误处理:")
    
    # 测试无效语言代码
    ms_translator = MicrosoftTranslatorEnhanced()
    
    try:
        result = ms_translator.translate_text("hello", "invalid-lang")
        print(f"   无效语言代码测试: {result}")
    except Exception as e:
        print(f"   无效语言代码处理: {e}")
    
    # 测试空文本
    result = ms_translator.translate_text("", "zh")
    print(f"   空文本处理: '{result}'")
    
    # 测试超长文本
    long_text = "Hello " * 100
    result = ms_translator.translate_text(long_text, "zh")
    print(f"   长文本处理: {result[:50]}...（已截断）")

def main():
    """主测试函数"""
    print("🧪 Microsoft Translator 增强版翻译器测试")
    print("=" * 60)
    
    # 配置指南
    test_configuration_guide()
    
    # 基础翻译测试
    test_enhanced_simple_translation()
    
    # 多语言支持测试
    test_language_support()
    
    # 错误处理测试
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n📋 总结:")
    print("   • Microsoft Translator API提供200万字符/月免费配额")
    print("   • 支持90+种语言的高质量翻译")
    print("   • 智能本地缓存减少API调用")
    print("   • 优雅的回退机制确保服务可用性")
    print("   • 完全兼容现有翻译器接口")

if __name__ == "__main__":
    main() 