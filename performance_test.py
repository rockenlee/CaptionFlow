#!/usr/bin/env python3
"""
翻译性能测试脚本
对比普通翻译器和优化版翻译器的性能差异
"""

import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from translator import Translator
from translator_optimized import OptimizedTranslator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_segments(count: int = 100):
    """创建测试段落数据"""
    test_texts = [
        "Hello, how are you today?",
        "This is a beautiful day.",
        "I love learning new things.",
        "Technology is advancing rapidly.",
        "The weather is very nice.",
        "Can you help me with this?",
        "I want to go home now.",
        "This movie is very interesting.",
        "Thank you for your help.",
        "Have a great day ahead.",
        "The food tastes delicious.",
        "I'm excited about this project.",
        "Learning languages is fun.",
        "The sunset looks amazing.",
        "I need to finish my work.",
        "Music makes me happy.",
        "Books are my best friends.",
        "Exercise keeps me healthy.",
        "Family time is precious.",
        "Dreams can come true."
    ]
    
    segments = []
    for i in range(count):
        text = test_texts[i % len(test_texts)]
        segments.append({
            'start': i * 2.0,
            'end': (i + 1) * 2.0,
            'text': f"{text} (Segment {i+1})"
        })
    
    return segments

def test_translator_performance(translator, segments, name):
    """测试翻译器性能"""
    print(f"\n{'='*50}")
    print(f"🧪 测试 {name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    if hasattr(translator, 'translate_segments_optimized'):
        # 优化版翻译器
        translations = translator.translate_segments_optimized(
            segments, 
            target_language='zh', 
            source_language='en'
        )
    else:
        # 普通翻译器
        translations = translator.translate_segments(
            segments, 
            target_language='zh', 
            source_language='en'
        )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"📊 性能结果:")
    print(f"  总耗时: {elapsed_time:.2f} 秒")
    print(f"  平均耗时: {elapsed_time/len(segments):.3f} 秒/段")
    print(f"  处理速度: {len(segments)/elapsed_time:.1f} 段/秒")
    print(f"  处理段落数: {len(segments)}")
    print(f"  成功翻译数: {len([t for t in translations if t and not t.startswith('[翻译失败]')])}")
    
    if hasattr(translator, 'get_performance_stats'):
        stats = translator.get_performance_stats()
        print(f"  缓存命中率: {stats['cache_hit_rate']}")
        print(f"  缓存大小: {stats['cache_size']}")
    
    return elapsed_time, translations

def run_performance_comparison():
    """运行性能对比测试"""
    print("🚀 CaptionFlow 翻译性能对比测试")
    print("="*60)
    
    # 测试配置
    test_configs = [
        {'segments': 50, 'name': '小规模测试 (50段)'},
        {'segments': 100, 'name': '中规模测试 (100段)'},
        {'segments': 200, 'name': '大规模测试 (200段)'}
    ]
    
    results = {}
    
    for config in test_configs:
        segment_count = config['segments']
        test_name = config['name']
        
        print(f"\n🎯 {test_name}")
        print("-" * 40)
        
        # 创建测试数据
        segments = create_test_segments(segment_count)
        
        # 测试普通翻译器 (Simple)
        try:
            normal_translator = Translator(service="simple")
            normal_time, normal_translations = test_translator_performance(
                normal_translator, segments, "普通翻译器 (Simple)"
            )
            results[f'normal_{segment_count}'] = normal_time
        except Exception as e:
            print(f"❌ 普通翻译器测试失败: {e}")
            normal_time = float('inf')
        
        # 测试优化版翻译器 (Simple)
        try:
            optimized_translator = OptimizedTranslator(service="simple", max_workers=10)
            optimized_time, optimized_translations = test_translator_performance(
                optimized_translator, segments, "优化版翻译器 (Simple)"
            )
            results[f'optimized_{segment_count}'] = optimized_time
        except Exception as e:
            print(f"❌ 优化版翻译器测试失败: {e}")
            optimized_time = float('inf')
        
        # 计算性能提升
        if normal_time != float('inf') and optimized_time != float('inf'):
            speedup = normal_time / optimized_time
            improvement = ((normal_time - optimized_time) / normal_time) * 100
            
            print(f"\n🎊 {test_name} 结果:")
            print(f"  性能提升: {speedup:.1f}x")
            print(f"  时间减少: {improvement:.1f}%")
            
            if speedup > 1:
                print(f"  ✅ 优化版更快，提升了 {speedup:.1f} 倍！")
            else:
                print(f"  ⚠️  普通版更快")
    
    # 总结报告
    print(f"\n{'='*60}")
    print("📈 性能测试总结报告")
    print(f"{'='*60}")
    
    for config in test_configs:
        segment_count = config['segments']
        test_name = config['name']
        
        normal_key = f'normal_{segment_count}'
        optimized_key = f'optimized_{segment_count}'
        
        if normal_key in results and optimized_key in results:
            normal_time = results[normal_key]
            optimized_time = results[optimized_key]
            speedup = normal_time / optimized_time
            
            print(f"\n{test_name}:")
            print(f"  普通版: {normal_time:.2f}秒")
            print(f"  优化版: {optimized_time:.2f}秒")
            print(f"  提升: {speedup:.1f}x")
    
    print(f"\n🎯 优化技术:")
    print(f"  ✅ 并行处理 - 多线程同时翻译")
    print(f"  ✅ 智能缓存 - 避免重复翻译")
    print(f"  ✅ 批量优化 - 减少API调用开销")
    print(f"  ✅ 无延迟等待 - Simple翻译无需等待")
    
    print(f"\n💡 建议:")
    print(f"  • 大量段落翻译时使用优化版")
    print(f"  • 重复内容多时缓存效果更好")
    print(f"  • Simple翻译优化效果最明显")
    print(f"  • 可根据硬件调整线程数")

if __name__ == "__main__":
    try:
        run_performance_comparison()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 性能测试结束") 