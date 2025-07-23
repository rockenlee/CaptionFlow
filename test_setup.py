#!/usr/bin/env python3
"""
CaptionFlow 功能测试脚本
验证核心组件是否正常工作
"""

import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        from caption_generator import CaptionGenerator
        print("✅ CaptionGenerator 导入成功")
    except Exception as e:
        print(f"❌ CaptionGenerator 导入失败: {e}")
        return False
    
    try:
        from translator import Translator
        print("✅ Translator 导入成功")
    except Exception as e:
        print(f"❌ Translator 导入失败: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
    except Exception as e:
        print(f"❌ Streamlit 导入失败: {e}")
        return False
    
    return True

def test_whisper_model():
    """测试Whisper模型加载"""
    print("\n🤖 测试Whisper模型...")
    
    try:
        from caption_generator import CaptionGenerator
        
        # 使用最小的模型进行测试
        caption_gen = CaptionGenerator(model_size="tiny")
        print("✅ Whisper tiny模型加载成功")
        
        # 清理
        caption_gen.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Whisper模型加载失败: {e}")
        return False

def test_translator():
    """测试翻译器"""
    print("\n🌍 测试翻译器...")
    
    try:
        from translator import Translator
        
        # 测试Simple翻译（默认，离线可用）
        translator = Translator(service="simple")
        
        # 测试语言检测功能
        target_lang = translator.detect_target_language("en")
        print(f"✅ 语言检测功能正常: en -> {target_lang}")
        
        # 测试语言名称获取
        lang_name = translator.get_language_name("zh")
        print(f"✅ 语言名称获取正常: zh -> {lang_name}")
        
        # 测试Simple翻译（基础词汇）
        translation = translator.translate_text("hello", "zh", "en")
        print(f"✅ Simple翻译（词典）: hello -> {translation}")
        
        # 测试Simple翻译（句子）
        sentence_translation = translator.translate_text("Hello world", "zh", "en")
        print(f"✅ Simple翻译（句子）: Hello world -> {sentence_translation}")
        
        # 可选：测试Google翻译（需要网络）
        try:
            google_translator = Translator(service="google")
            google_translation = google_translator.translate_text("hello", "zh", "en")
            print(f"✅ Google翻译功能正常: hello -> {google_translation}")
        except Exception as e:
            print(f"⚠️  Google翻译测试失败（可能网络问题）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 翻译器测试失败: {e}")
        return False

def test_optimized_translator():
    """测试优化版翻译器"""
    print("\n⚡ 测试优化版翻译器...")
    
    try:
        from translator_optimized import OptimizedTranslator
        
        # 测试优化版Simple翻译器
        optimized_translator = OptimizedTranslator(service="simple", max_workers=5)
        
        # 创建少量测试段落
        test_segments = [
            {'start': 0, 'end': 2, 'text': 'Hello world'},
            {'start': 2, 'end': 4, 'text': 'Thank you'},
            {'start': 4, 'end': 6, 'text': 'Good morning'},
            {'start': 6, 'end': 8, 'text': 'Have a nice day'},
            {'start': 8, 'end': 10, 'text': 'See you later'}
        ]
        
        # 测试并行翻译
        import time
        start_time = time.time()
        translations = optimized_translator.translate_segments_optimized(
            test_segments, target_language='zh', source_language='en'
        )
        elapsed_time = time.time() - start_time
        
        print(f"✅ 优化版翻译器工作正常")
        print(f"  处理了 {len(test_segments)} 个段落")
        print(f"  耗时: {elapsed_time:.3f}秒")
        print(f"  速度: {len(test_segments)/elapsed_time:.1f}段/秒")
        
        # 测试性能统计
        stats = optimized_translator.get_performance_stats()
        print(f"  缓存命中率: {stats['cache_hit_rate']}")
        
        return True
        
    except ImportError:
        print("❌ 优化版翻译器模块导入失败")
        return False
    except Exception as e:
        print(f"❌ 优化版翻译器测试失败: {e}")
        return False

def test_dependencies():
    """测试关键依赖"""
    print("\n📦 测试关键依赖...")
    
    dependencies = [
        'faster_whisper',
        'openai',
        'moviepy',
        'srt',
        'langdetect',
        'requests',
        'streamlit'
    ]
    
    all_good = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep}: {e}")
            all_good = False
    
    return all_good

def test_i18n():
    """测试国际化功能"""
    print("\n🌐 测试国际化功能...")
    
    try:
        from i18n import i18n
        
        # 测试可用语言数量
        languages = i18n.get_available_languages()
        print(f"✅ 支持 {len(languages)} 种界面语言")
        
        # 测试几种语言的翻译
        test_languages = ["zh_CN", "en_US", "es_ES", "ja_JP"]
        for lang_code in test_languages:
            i18n.set_language(lang_code)
            title = i18n.t("app.title")
            print(f"  ✅ {languages[lang_code]}: {title[:40]}...")
        
        # 测试翻译键不存在的情况
        missing_key = i18n.t("non.existent.key")
        print(f"✅ 缺失键处理正常: {missing_key}")
        
        return True
        
    except ImportError:
        print("❌ 国际化模块导入失败")
        return False
    except Exception as e:
        print(f"❌ 国际化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎬 CaptionFlow 功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("关键依赖", test_dependencies),
        ("Whisper模型", test_whisper_model),
        ("翻译器", test_translator),
        ("优化版翻译器", test_optimized_translator),
        ("国际化", test_i18n),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！CaptionFlow 已准备就绪")
        print("\n🚀 启动服务:")
        print("   Web界面: streamlit run app.py")
        print("   访问地址: http://localhost:8501")
        print("   命令行: python main.py -i your_video.mp4 --bilingual")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 