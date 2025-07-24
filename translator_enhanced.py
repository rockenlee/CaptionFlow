"""
增强版翻译器 - 使用Microsoft Translator API替代Simple翻译
免费配额：200万字符/月，比其他服务更大
"""

import requests
import json
import uuid
import logging
import time
import os
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import hashlib

# 设置日志
logger = logging.getLogger(__name__)

class MicrosoftTranslatorEnhanced:
    """增强版翻译器 - 使用Microsoft Translator API"""
    
    def __init__(self, api_key: Optional[str] = None, region: str = "global", max_workers: int = 10):
        """
        初始化Microsoft Translator增强版翻译器
        
        Args:
            api_key: Azure Translator API密钥（可选，使用免费层）
            region: Azure区域，默认global
            max_workers: 并行翻译的最大线程数
        """
        self.api_key = api_key or os.getenv('AZURE_TRANSLATOR_KEY')
        self.region = region
        self.max_workers = max_workers
        
        # Microsoft Translator API配置
        self.base_url = "https://api.cognitive.microsofttranslator.com"
        self.translate_url = f"{self.base_url}/translate"
        
        # 翻译缓存
        self.translation_cache = {}
        
        # 性能统计
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_translations': 0,
            'api_calls': 0,
            'characters_translated': 0
        }
        
        # 支持的语言映射
        self.language_map = {
            'zh': 'zh-Hans',
            'zh-CN': 'zh-Hans', 
            'zh-TW': 'zh-Hant',
            'chinese': 'zh-Hans',
            'en': 'en',
            'english': 'en',
            'ja': 'ja',
            'japanese': 'ja',
            'ko': 'ko',
            'korean': 'ko',
            'fr': 'fr',
            'french': 'fr',
            'de': 'de',
            'german': 'de',
            'es': 'es',
            'spanish': 'es',
            'ru': 'ru',
            'russian': 'ru',
            'pt': 'pt',
            'portuguese': 'pt',
            'it': 'it',
            'italian': 'it',
            'ar': 'ar',
            'arabic': 'ar',
            'hi': 'hi',
            'hindi': 'hi'
        }
        
        # 初始化本地词典作为补充
        self._init_local_dictionary()
        
        logger.info("Microsoft Translator增强版翻译器初始化完成")
    
    def _init_local_dictionary(self):
        """初始化本地词典作为API的补充"""
        self.local_dict = {
            # 常用词汇（作为缓存和备用）
            'hello': '你好',
            'world': '世界',
            'thank you': '谢谢',
            'good': '好',
            'bad': '坏',
            'yes': '是',
            'no': '不',
            'please': '请',
            'sorry': '对不起',
            'welcome': '欢迎',
            'goodbye': '再见',
            'how are you': '你好吗',
            'what is your name': '你叫什么名字',
            'nice to meet you': '很高兴认识你',
            'see you later': '回头见',
            'good morning': '早上好',
            'good afternoon': '下午好',
            'good evening': '晚上好',
            'good night': '晚安'
        }
    
    def _get_cache_key(self, text: str, target_lang: str, source_lang: str = "") -> str:
        """生成缓存键"""
        cache_input = f"{text}|{target_lang}|{source_lang}|microsoft"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _normalize_language_code(self, language_code: str) -> str:
        """标准化语言代码为Microsoft Translator格式"""
        if not language_code:
            return 'en'
        
        normalized = self.language_map.get(language_code.lower(), language_code)
        return normalized
    
    def _translate_with_local_dict(self, text: str, target_language: str) -> Optional[str]:
        """使用本地词典进行翻译（快速缓存）"""
        text_lower = text.lower().strip()
        
        if target_language in ['zh', 'zh-Hans', 'chinese']:
            return self.local_dict.get(text_lower)
        
        return None
    
    def _call_microsoft_api(self, texts: List[str], target_language: str, source_language: str = "") -> List[str]:
        """调用Microsoft Translator API"""
        try:
            # 标准化语言代码
            target_lang = self._normalize_language_code(target_language)
            source_lang = self._normalize_language_code(source_language) if source_language else None
            
            # 构建请求
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key or '',
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            # 构建请求体
            body = [{'text': text} for text in texts]
            
            # 构建URL参数
            params = {
                'api-version': '3.0',
                'to': target_lang
            }
            
            if source_lang:
                params['from'] = source_lang
            
            # 发送请求
            response = requests.post(
                self.translate_url, 
                params=params, 
                headers=headers, 
                json=body,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = []
                
                for item in result:
                    if 'translations' in item and len(item['translations']) > 0:
                        translated_text = item['translations'][0]['text']
                        translations.append(translated_text)
                    else:
                        translations.append(texts[len(translations)])  # 返回原文
                
                # 更新统计
                self.stats['api_calls'] += 1
                self.stats['characters_translated'] += sum(len(text) for text in texts)
                
                return translations
            
            else:
                logger.error(f"Microsoft Translator API错误: {response.status_code} - {response.text}")
                return texts  # 返回原文
                
        except Exception as e:
            logger.error(f"Microsoft Translator API调用失败: {e}")
            return texts  # 返回原文
    
    def translate_text(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        翻译单个文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言（可选）
            
        Returns:
            翻译后的文本
        """
        if not text.strip():
            return text
        
        # 检查缓存
        cache_key = self._get_cache_key(text, target_language, source_language)
        if cache_key in self.translation_cache:
            self.stats['cache_hits'] += 1
            return self.translation_cache[cache_key]
        
        self.stats['cache_misses'] += 1
        self.stats['total_translations'] += 1
        
        # 1. 尝试本地词典
        local_result = self._translate_with_local_dict(text, target_language)
        if local_result:
            self.translation_cache[cache_key] = local_result
            return local_result
        
        # 2. 使用Microsoft Translator API
        if self.api_key:  # 只有在有API密钥时才调用
            try:
                results = self._call_microsoft_api([text], target_language, source_language)
                if results and len(results) > 0:
                    translated_text = results[0]
                    self.translation_cache[cache_key] = translated_text
                    return translated_text
            except Exception as e:
                logger.error(f"Microsoft API翻译失败: {e}")
        
        # 3. 回退到简单标记
        if target_language in ['zh', 'zh-Hans', 'chinese']:
            fallback = f"[中译] {text}"
        else:
            fallback = f"[{target_language}] {text}"
        
        self.translation_cache[cache_key] = fallback
        return fallback
    
    def translate_batch(self, texts: List[str], target_language: str, source_language: str = "") -> List[str]:
        """
        批量翻译文本
        
        Args:
            texts: 要翻译的文本列表
            target_language: 目标语言
            source_language: 源语言（可选）
            
        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []
        
        # 过滤缓存命中的文本
        uncached_texts = []
        results = [''] * len(texts)
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if not text.strip():
                results[i] = text
                continue
            
            cache_key = self._get_cache_key(text, target_language, source_language)
            if cache_key in self.translation_cache:
                results[i] = self.translation_cache[cache_key]
                self.stats['cache_hits'] += 1
            else:
                # 先尝试本地词典
                local_result = self._translate_with_local_dict(text, target_language)
                if local_result:
                    results[i] = local_result
                    self.translation_cache[cache_key] = local_result
                    self.stats['cache_hits'] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
                    self.stats['cache_misses'] += 1
        
        # 批量翻译未缓存的文本
        if uncached_texts and self.api_key:
            try:
                # Microsoft Translator API支持批量翻译，但建议每批不超过100个
                batch_size = 50
                translated_results = []
                
                for i in range(0, len(uncached_texts), batch_size):
                    batch = uncached_texts[i:i + batch_size]
                    batch_translations = self._call_microsoft_api(batch, target_language, source_language)
                    translated_results.extend(batch_translations)
                
                # 更新结果和缓存
                for i, translated_text in enumerate(translated_results):
                    if i < len(uncached_indices):
                        idx = uncached_indices[i]
                        results[idx] = translated_text
                        
                        # 更新缓存
                        original_text = uncached_texts[i]
                        cache_key = self._get_cache_key(original_text, target_language, source_language)
                        self.translation_cache[cache_key] = translated_text
                        
            except Exception as e:
                logger.error(f"批量翻译失败: {e}")
                # 回退处理
                for i, idx in enumerate(uncached_indices):
                    if i < len(uncached_texts):
                        fallback = f"[{target_language}] {uncached_texts[i]}"
                        results[idx] = fallback
        
        # 如果没有API密钥，使用回退方案
        elif uncached_texts:
            for i, idx in enumerate(uncached_indices):
                if i < len(uncached_texts):
                    if target_language in ['zh', 'zh-Hans', 'chinese']:
                        fallback = f"[中译] {uncached_texts[i]}"
                    else:
                        fallback = f"[{target_language}] {uncached_texts[i]}"
                    results[idx] = fallback
        
        self.stats['total_translations'] += len(texts)
        return results
    
    def parallel_translate(self, texts: List[str], target_language: str, source_language: str = "", 
                          progress_callback=None) -> List[str]:
        """
        并行翻译大量文本
        
        Args:
            texts: 要翻译的文本列表
            target_language: 目标语言
            source_language: 源语言（可选）
            progress_callback: 进度回调函数
            
        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []
        
        # 分批处理
        batch_size = 20  # 每个线程处理20个文本
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        results = [''] * len(texts)
        
        def translate_batch_worker(batch_info):
            batch_idx, batch_texts = batch_info
            start_idx = batch_idx * batch_size
            batch_results = self.translate_batch(batch_texts, target_language, source_language)
            return start_idx, batch_results
        
        # 并行执行
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(batches))) as executor:
            # 提交任务
            futures = [
                executor.submit(translate_batch_worker, (i, batch)) 
                for i, batch in enumerate(batches)
            ]
            
            # 收集结果
            completed_batches = 0
            for future in as_completed(futures):
                try:
                    start_idx, batch_results = future.result()
                    
                    # 更新结果
                    for i, result in enumerate(batch_results):
                        if start_idx + i < len(results):
                            results[start_idx + i] = result
                    
                    completed_batches += 1
                    
                    # 进度回调
                    if progress_callback:
                        progress = (completed_batches / len(batches)) * 100
                        progress_callback(completed_batches * batch_size, len(texts), progress)
                        
                except Exception as e:
                    logger.error(f"并行翻译任务失败: {e}")
        
        return results
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_translations': self.stats['total_translations'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'api_calls': self.stats['api_calls'],
            'characters_translated': self.stats['characters_translated'],
            'average_chars_per_api_call': (
                self.stats['characters_translated'] / self.stats['api_calls'] 
                if self.stats['api_calls'] > 0 else 0
            )
        }
    
    def get_language_name(self, language_code: str) -> str:
        """获取语言名称"""
        language_names = {
            'zh': '中文', 'zh-Hans': '中文', 'zh-Hant': '繁体中文',
            'en': '英文', 'ja': '日文', 'ko': '韩文',
            'fr': '法文', 'de': '德文', 'es': '西班牙文', 
            'ru': '俄文', 'pt': '葡萄牙文', 'it': '意大利文',
            'ar': '阿拉伯文', 'hi': '印地文'
        }
        return language_names.get(language_code, language_code)

# 使用示例和测试函数
def test_microsoft_translator():
    """测试Microsoft Translator增强版翻译器"""
    print("🧪 测试Microsoft Translator增强版翻译器")
    
    # 不提供API密钥的测试（使用本地词典和回退）
    translator = MicrosoftTranslatorEnhanced()
    
    test_texts = [
        "hello",
        "world", 
        "thank you",
        "This is a more complex sentence that requires API translation.",
        "How are you today?",
        "Machine translation is improving rapidly."
    ]
    
    print("\n📝 单个翻译测试:")
    for text in test_texts[:3]:  # 只测试本地词典部分
        result = translator.translate_text(text, "zh")
        print(f"  {text} -> {result}")
    
    print("\n📦 批量翻译测试:")
    batch_results = translator.translate_batch(test_texts, "zh")
    for original, translated in zip(test_texts, batch_results):
        print(f"  {original} -> {translated}")
    
    print("\n📊 性能统计:")
    stats = translator.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n💡 提示: 设置AZURE_TRANSLATOR_KEY环境变量以启用完整API功能")

if __name__ == "__main__":
    test_microsoft_translator() 