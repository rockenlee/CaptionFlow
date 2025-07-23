#!/usr/bin/env python3
"""
测试国际化功能
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from i18n import i18n

def test_i18n():
    """测试国际化功能"""
    print("🌍 国际化功能测试")
    print("=" * 50)
    
    # 测试所有支持的语言
    languages = i18n.get_available_languages()
    print(f"📊 支持的语言数量: {len(languages)}")
    
    for lang_code, lang_name in languages.items():
        print(f"  • {lang_code}: {lang_name}")
    
    print("\n" + "=" * 50)
    
    # 测试不同语言的翻译
    test_keys = [
        "app.title",
        "app.subtitle", 
        "sidebar.settings",
        "sidebar.model_selection",
        "languages.zh",
        "languages.en",
        "processing.extracting_audio",
        "processing.completed",
        "errors.processing_failed"
    ]
    
    for lang_code in ["zh_CN", "en_US", "es_ES", "ar_SA", "ja_JP"]:
        print(f"\n🔤 {languages[lang_code]} ({lang_code}):")
        print("-" * 30)
        
        i18n.set_language(lang_code)
        
        for key in test_keys:
            translation = i18n.t(key)
            print(f"  {key}: {translation}")
    
    print("\n" + "=" * 50)
    print("✅ 国际化测试完成")

if __name__ == "__main__":
    test_i18n() 